#!/usr/bin/env python3
"""
Comprehensive test suite for Dehashed API tool.

This test suite covers:
1. API key retrieval from environment variables and config files
2. Rate-limit handler with mocked HTTP requests
3. CSV/PDF export functions with file existence verification
4. Dry-run mode with mocked API responses
"""

import os
import sys
import tempfile
import unittest
import pandas as pd
import json
from unittest.mock import patch, MagicMock, mock_open
from configparser import NoSectionError, NoOptionError
from rich.console import Console

# Import modules to test
from get_api_key import get_api_key
from dehashed import search, DeHashedError, DeHashedRateLimitError, DeHashedAPIError
from pdf_generator import generate_pdf_report, create_pdf_from_csv, extract_metadata_from_filename
from result_extraction import extract_email_password_data, print_extraction_summary

console = Console()


class TestAPIKeyRetrieval(unittest.TestCase):
    """Test API key retrieval from various sources."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment variable if it exists
        if 'DEHASHED_API_KEY' in os.environ:
            del os.environ['DEHASHED_API_KEY']
    
    def test_api_key_from_environment_variable(self):
        """Test API key retrieval from environment variable."""
        test_key = 'test_env_api_key_123'
        with patch.dict(os.environ, {'DEHASHED_API_KEY': test_key}):
            result = get_api_key()
            self.assertEqual(result, test_key)
            console.print("[green]✅ API key from environment variable test passed[/green]")
    
    def test_api_key_from_config_file(self):
        """Test API key retrieval from config.ini file."""
        test_key = 'test_config_api_key_456'
        
        # Mock ConfigParser
        with patch('get_api_key.ConfigParser') as MockConfigParser:
            mock_config = MockConfigParser.return_value
            mock_config.read.return_value = None
            mock_config.get.return_value = test_key
            
            # Clear environment variable for this test
            with patch.dict(os.environ, {}, clear=True):
                result = get_api_key()
                self.assertEqual(result, test_key)
                mock_config.get.assert_called_once_with('DEFAULT', 'DEHASHED_API_KEY')
                console.print("[green]✅ API key from config file test passed[/green]")
    
    def test_api_key_not_found(self):
        """Test behavior when API key is not found in any source."""
        with patch('get_api_key.ConfigParser') as MockConfigParser:
            mock_config = MockConfigParser.return_value
            mock_config.read.return_value = None
            mock_config.get.side_effect = NoSectionError('DEFAULT')
            
            # Clear environment variable for this test
            with patch.dict(os.environ, {}, clear=True):
                result = get_api_key()
                self.assertIsNone(result)
                console.print("[green]✅ API key not found test passed[/green]")
    
    def test_api_key_priority_env_over_config(self):
        """Test that environment variable takes priority over config file."""
        env_key = 'env_key_priority'
        config_key = 'config_key_fallback'
        
        with patch('get_api_key.ConfigParser') as MockConfigParser:
            mock_config = MockConfigParser.return_value
            mock_config.read.return_value = None
            mock_config.get.return_value = config_key
            
            with patch.dict(os.environ, {'DEHASHED_API_KEY': env_key}):
                result = get_api_key()
                self.assertEqual(result, env_key)
                # Config should not be called when env var is present
                mock_config.get.assert_not_called()
                console.print("[green]✅ API key priority test passed[/green]")


class TestRateLimitHandler(unittest.TestCase):
    """Test rate-limiting functionality with mocked HTTP requests."""
    
    @patch('dehashed.requests.post')
    @patch('dehashed.time.sleep')  # Mock sleep to speed up tests
    def test_rate_limit_with_retry_after_header(self, mock_sleep, mock_post):
        """Test rate limit handling with Retry-After header."""
        # First call returns 429, second returns 200
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'Retry-After': '2'}
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'success': True, 'entries': []}
        
        mock_post.side_effect = [mock_response_429, mock_response_200]
        
        result = search(query='test@example.com', api_key='test_key', max_retries=1)
        
        self.assertEqual(result, {'success': True, 'entries': []})
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once_with(2)  # Should sleep for Retry-After duration
        console.print("[green]✅ Rate limit with Retry-After header test passed[/green]")
    
    @patch('dehashed.requests.post')
    @patch('dehashed.time.sleep')
    def test_rate_limit_exponential_backoff(self, mock_sleep, mock_post):
        """Test rate limit handling with exponential backoff."""
        # First call returns 429 without Retry-After, second returns 200
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {}  # No Retry-After header
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'success': True, 'entries': []}
        
        mock_post.side_effect = [mock_response_429, mock_response_200]
        
        result = search(query='test@example.com', api_key='test_key', max_retries=1)
        
        self.assertEqual(result, {'success': True, 'entries': []})
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once_with(1)  # Should use base delay for first retry
        console.print("[green]✅ Rate limit exponential backoff test passed[/green]")
    
    @patch('dehashed.requests.post')
    def test_rate_limit_max_retries_exceeded(self, mock_post):
        """Test that DeHashedRateLimitError is raised when max retries exceeded."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '1'}
        mock_post.return_value = mock_response
        
        with self.assertRaises(DeHashedRateLimitError) as context:
            search(query='test@example.com', api_key='test_key', max_retries=0)
        
        self.assertIn('Rate limit exceeded', str(context.exception))
        console.print("[green]✅ Rate limit max retries exceeded test passed[/green]")
    
    @patch('dehashed.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test handling of non-rate-limit API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_post.return_value = mock_response
        
        with self.assertRaises(DeHashedAPIError) as context:
            search(query='test@example.com', api_key='invalid_key')
        
        self.assertIn('401', str(context.exception))
        self.assertIn('Unauthorized', str(context.exception))
        console.print("[green]✅ API error handling test passed[/green]")


class TestCSVPDFExportFunctions(unittest.TestCase):
    """Test CSV and PDF export functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, '2024-01-15_test_domain.com.csv')
        self.pdf_file = os.path.join(self.test_dir, '2024-01-15_test_domain.com.pdf')
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_csv_file_creation_and_existence(self):
        """Test CSV file creation and existence verification."""
        # Create sample data
        sample_data = {
            'email': ['user1@example.com', 'user2@test.org', 'admin@company.net'],
            'password': ['password123', 'secret456', 'admin789']
        }
        df = pd.DataFrame(sample_data)
        
        # Save to CSV
        df.to_csv(self.csv_file, index=False)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.csv_file))
        
        # Verify file content
        loaded_df = pd.read_csv(self.csv_file)
        self.assertEqual(len(loaded_df), 3)
        self.assertListEqual(list(loaded_df.columns), ['email', 'password'])
        console.print("[green]✅ CSV file creation and existence test passed[/green]")
    
    def test_pdf_generation_from_csv(self):
        """Test PDF generation from CSV file."""
        # Create sample CSV file
        sample_data = {
            'email': ['user1@example.com', 'user2@test.org'],
            'password': ['password123', 'secret456']
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(self.csv_file, index=False)
        
        # Generate PDF
        pdf_path = create_pdf_from_csv(self.csv_file, self.pdf_file)
        
        # Verify PDF exists
        self.assertTrue(os.path.exists(pdf_path))
        self.assertEqual(pdf_path, self.pdf_file)
        
        # Verify PDF file size is reasonable (not empty)
        pdf_size = os.path.getsize(pdf_path)
        self.assertGreater(pdf_size, 1000)  # Should be at least 1KB
        console.print("[green]✅ PDF generation from CSV test passed[/green]")
    
    def test_metadata_extraction_from_filename(self):
        """Test metadata extraction from CSV filename."""
        test_filename = '2024-01-15_example_domain.com.csv'
        metadata = extract_metadata_from_filename(test_filename)
        
        self.assertEqual(metadata['date'], '2024-01-15')
        self.assertEqual(metadata['query'], 'example domain.com')
        self.assertEqual(metadata['filename'], test_filename)
        console.print("[green]✅ Metadata extraction test passed[/green]")
    
    def test_pdf_generation_with_generate_pdf_report(self):
        """Test high-level PDF generation function."""
        # Create sample CSV file
        sample_data = {
            'email': ['test@example.com'],
            'password': ['testpass']
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(self.csv_file, index=False)
        
        # Use high-level function
        with patch('pdf_generator.console'):
            pdf_path = generate_pdf_report(self.csv_file)
        
        # Verify PDF exists
        self.assertTrue(os.path.exists(pdf_path))
        console.print("[green]✅ High-level PDF generation test passed[/green]")
    
    def test_csv_not_found_error(self):
        """Test error handling when CSV file doesn't exist."""
        non_existent_file = os.path.join(self.test_dir, 'non_existent.csv')
        
        with self.assertRaises(FileNotFoundError):
            create_pdf_from_csv(non_existent_file)
        console.print("[green]✅ CSV not found error test passed[/green]")


class TestDryRunMode(unittest.TestCase):
    """Test dry-run functionality with mocked API responses."""
    
    @patch('dehashed.requests.post')
    def test_dry_run_successful_search(self, mock_post):
        """Test dry-run mode with successful API response."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'total': 2,
            'entries': [
                {
                    'id': '1',
                    'email': 'user1@example.com',
                    'password': 'password123',
                    'username': 'user1',
                    'domain': 'example.com'
                },
                {
                    'id': '2',
                    'email': 'user2@example.com',
                    'password': 'secret456',
                    'username': 'user2',
                    'domain': 'example.com'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Perform search
        result = search(query='example.com', api_key='dry_run_key')
        
        # Verify response structure
        self.assertTrue(result['success'])
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['entries']), 2)
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['query'], 'example.com')
        self.assertEqual(call_args[1]['auth'], ('dry_run_key', ''))
        
        console.print("[green]✅ Dry-run successful search test passed[/green]")
    
    @patch('dehashed.requests.post')
    def test_dry_run_with_result_extraction(self, mock_post):
        """Test dry-run mode with result extraction."""
        # Mock API response with mixed data quality
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'total': 4,
            'entries': [
                {
                    'id': '1',
                    'email': 'user1@example.com',
                    'password': 'password123',
                    'username': 'user1'
                },
                {
                    'id': '2',
                    'email': 'user2@example.com',
                    'password': '',  # Empty password - should be filtered
                    'username': 'user2'
                },
                {
                    'id': '3',
                    'email': None,  # Null email - should be filtered
                    'password': 'secret456',
                    'username': 'user3'
                },
                {
                    'id': '4',
                    'email': 'user4@example.com',
                    'password': 'admin789',
                    'username': 'user4'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Perform search and extract data
        api_response = search(query='example.com', api_key='dry_run_key')
        df = extract_email_password_data(api_response)
        
        # Verify extracted data (should only have valid email/password pairs)
        self.assertEqual(len(df), 2)  # Only 2 valid pairs
        self.assertListEqual(list(df['email']), ['user1@example.com', 'user4@example.com'])
        self.assertListEqual(list(df['password']), ['password123', 'admin789'])
        
        console.print("[green]✅ Dry-run with result extraction test passed[/green]")
    
    @patch('dehashed.requests.post')
    def test_dry_run_mock_api_without_real_request(self, mock_post):
        """Test completely mocked API without any real network requests."""
        # Mock the requests.post to return our desired response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'total': 1,
            'entries': [
                {
                    'id': 'mock_1',
                    'email': 'test@mockdomain.com',
                    'password': 'mock_password',
                    'username': 'mock_user',
                    'domain': 'mockdomain.com'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Test the search function with mocked requests
        result = search(query='mockdomain.com', api_key='no_real_key')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['entries'][0]['email'], 'test@mockdomain.com')
        self.assertEqual(result['entries'][0]['password'], 'mock_password')
        
        console.print("[green]✅ Dry-run completely mocked API test passed[/green]")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('dehashed.requests.post')
    def test_end_to_end_workflow(self, mock_post):
        """Test complete workflow from API call to PDF generation."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'total': 2,
            'entries': [
                {
                    'id': '1',
                    'email': 'user1@testdomain.com',
                    'password': 'password123'
                },
                {
                    'id': '2',
                    'email': 'user2@testdomain.com',
                    'password': 'secret456'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Step 1: API search
        api_response = search(query='testdomain.com', api_key='test_key')
        
        # Step 2: Extract data
        df = extract_email_password_data(api_response)
        self.assertEqual(len(df), 2)
        
        # Step 3: Save to CSV
        csv_file = os.path.join(self.test_dir, '2024-01-15_testdomain.com.csv')
        df.to_csv(csv_file, index=False)
        self.assertTrue(os.path.exists(csv_file))
        
        # Step 4: Generate PDF
        with patch('pdf_generator.console'):
            pdf_file = generate_pdf_report(csv_file)
        self.assertTrue(os.path.exists(pdf_file))
        
        console.print("[green]✅ End-to-end workflow test passed[/green]")


def run_all_tests():
    """Run all tests with detailed output."""
    console.print("[bold cyan]🧪 Running Dehashed API Tool Test Suite[/bold cyan]\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAPIKeyRetrieval,
        TestRateLimitHandler,
        TestCSVPDFExportFunctions,
        TestDryRunMode,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    console.print(f"\n[bold]Test Summary:[/bold]")
    console.print(f"  • Tests run: [cyan]{result.testsRun}[/cyan]")
    console.print(f"  • Failures: [red]{len(result.failures)}[/red]")
    console.print(f"  • Errors: [red]{len(result.errors)}[/red]")
    
    if result.wasSuccessful():
        console.print(f"\n[bold green]✅ All tests passed successfully![/bold green]")
    else:
        console.print(f"\n[bold red]❌ Some tests failed. Check output above.[/bold red]")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Check if we should run individual tests or all tests
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        success = run_all_tests()
        sys.exit(0 if success else 1)
    else:
        unittest.main()
