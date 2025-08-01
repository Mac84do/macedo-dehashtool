#!/usr/bin/env python3
"""
Integration test for main_v2.py with mocked DeHashed API via requests-mock.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests_mock
from main_v2 import perform_api_search
import tempfile

class TestMainV2Integration(unittest.TestCase):
    @requests_mock.Mocker()
    def test_main_v2_integration(self, mock_request):
        """Test main_v2.py integration with mocked DeHashed API."""
        # Mock the API response
        mock_request.post('https://api.dehashed.com/v2/search', json={
            'success': True,
            'entries': [
                {'email': 'test@example.com', 'password': 'pass123'}
            ]
        })

        # Use a temporary directory for output to avoid filesystem conflicts
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock file operations to avoid actual file creation
            with patch('pandas.DataFrame.to_csv') as mock_to_csv:
                with patch('main_v2.generate_pdf_report') as mock_pdf:
                    with patch('main_v2.console') as mock_console:
                        with patch('rich.prompt.Confirm.ask', return_value=False) as mock_confirm:
                            mock_pdf.return_value = f'{temp_dir}/test.pdf'
                            
                            # Run the function
                            perform_api_search('1', 'example.com', 'test@example.com', 'dummy_key')
                        
                        # Check that CSV was attempted to be saved
                        mock_to_csv.assert_called_once()
                        
                        # Verify API was called
                        self.assertEqual(mock_request.call_count, 1)
                        
                        # Verify the request was made correctly
                        history = mock_request.request_history
                        self.assertEqual(history[0].method, 'POST')
                        self.assertEqual(history[0].url, 'https://api.dehashed.com/v2/search')
                        
                        # Verify that console print was called (successful execution)
                        self.assertTrue(mock_console.print.called, "Console should have been used for output")

if __name__ == '__main__':
    unittest.main()

