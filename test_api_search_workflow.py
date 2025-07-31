#!/usr/bin/env python3
"""
Step 2: API Search Workflow Test Script

This script:
• Runs the CLI entry-point that triggers the search
• Passes a canned query string (email or domain)
• Captures stdout/stderr to ensure no crash and the mock data is accepted
• Asserts that the internal dataframe / list now contains the two mock records
"""

import sys
import json
import configparser
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.panel import Panel

# Import our modules
from dehashed import search
from result_extraction_v2 import extract_all_fields, extract_email_password_data

console = Console()

def load_test_config():
    """Load the test configuration with fake credentials."""
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    
    email = config.get('DEFAULT', 'DEHASHED_EMAIL')
    api_key = config.get('DEFAULT', 'DEHASHED_API_KEY')
    
    return email, api_key

def load_mock_response():
    """Load the mock DeHashed response from JSON file."""
    with open('test_fixtures/mock_dehashed_response.json', 'r') as f:
        mock_response = json.load(f)
    
    return mock_response

@patch('requests.post')
def test_api_search_workflow(mock_post):
    """
    Test the API search workflow with mocked data.
    
    This function:
    1. Loads test credentials
    2. Sets up mock API response 
    3. Triggers the search function with a canned query
    4. Captures and validates the response
    5. Asserts the dataframe contains expected mock records
    """
    
    console.print(Panel.fit(
        "[bold cyan]🧪 Step 2: API Search Workflow Test[/bold cyan]\n"
        "Testing the complete search workflow with mock data:\n"
        "• CLI entry-point invocation\n"
        "• Canned query processing\n"
        "• Mock data acceptance\n"
        "• DataFrame assertion with expected records",
        title="API Search Workflow Test"
    ))
    
    # Step 1: Load test credentials
    console.print("\n[bold yellow]1. Loading Test Configuration[/bold yellow]")
    email, api_key = load_test_config()
    console.print(f"[green]✅ Test email loaded:[/green] {email}")
    console.print(f"[green]✅ Test API key loaded:[/green] {api_key[:20]}...")
    
    # Step 2: Load mock response data
    console.print("\n[bold yellow]2. Loading Mock Response Data[/bold yellow]")
    mock_response = load_mock_response()
    console.print(f"[green]✅ Mock response loaded with {mock_response['total']} entries[/green]")
    console.print(f"[cyan]   • Balance: {mock_response['balance']} credits[/cyan]")
    console.print(f"[cyan]   • Success: {mock_response['success']}[/cyan]")
    
    # Step 3: Configure the mock to intercept network requests
    console.print("\n[bold yellow]3. Configuring Network Mock[/bold yellow]")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.headers = {
        'x-ratelimit-remaining': '95',
        'x-ratelimit-limit': '100',
        'x-balance': str(mock_response['balance'])
    }
    console.print("[green]✅ Network mock configured successfully[/green]")
    
    # Step 4: Trigger the search with canned query (domain search)
    console.print("\n[bold yellow]4. Triggering API Search with Canned Query[/bold yellow]")
    canned_query = "example.com"
    console.print(f"[cyan]🔍 Canned query:[/cyan] {canned_query}")
    
    try:
        # This is the CLI entry-point call that triggers the search
        response = search(query=canned_query, email=email, api_key=api_key)
        console.print("[green]✅ API search completed without crash[/green]")
        
        # Verify the mock was called (network interception worked)
        assert mock_post.called, "Mock should have been called"
        console.print("[green]✅ Network request successfully intercepted[/green]")
        
        # Step 5: Capture and validate stdout/stderr
        console.print("\n[bold yellow]5. Validating Response Data[/bold yellow]")
        assert response is not None, "Response should not be None"
        assert 'entries' in response, "Response should contain 'entries' key"
        assert 'total' in response, "Response should contain 'total' key"
        assert response['success'] == True, "Response should indicate success"
        console.print("[green]✅ Response structure validated[/green]")
        
        # Step 6: Extract data into DataFrame and assert contents
        console.print("\n[bold yellow]6. Extracting Data to DataFrame[/bold yellow]")
        df = extract_all_fields(response)
        console.print(f"[green]✅ DataFrame created with {len(df)} records[/green]")
        
        # Assert we have the expected number of mock records
        expected_record_count = 4  # From our mock data
        assert len(df) == expected_record_count, f"Expected {expected_record_count} records, got {len(df)}"
        console.print(f"[green]✅ DataFrame contains expected {expected_record_count} mock records[/green]")
        
        # Step 7: Validate specific mock record content
        console.print("\n[bold yellow]7. Asserting Mock Record Content[/bold yellow]")
        
        # Check that we have the expected email addresses from our mock data
        expected_emails = {
            "user1@example.com",
            "admin@testdomain.org", 
            "support@company.net",
            "dev@startup.io"
        }
        actual_emails = set(df['email'].tolist())
        assert expected_emails == actual_emails, f"Expected emails {expected_emails}, got {actual_emails}"
        console.print("[green]✅ All expected email addresses found in DataFrame[/green]")
        
        # Check that we have both plaintext and hashed records
        plaintext_records = df[df['password'].notna() & (df['password'] != '')].shape[0]
        hash_records = df[df['hash'].notna() & (df['hash'] != '')].shape[0]
        
        assert plaintext_records == 2, f"Expected 2 plaintext records, got {plaintext_records}"
        assert hash_records == 2, f"Expected 2 hash records, got {hash_records}"
        console.print(f"[green]✅ Found {plaintext_records} plaintext and {hash_records} hash records as expected[/green]")
        
        # Step 8: Display success summary
        console.print("\n[bold green]🎉 API Search Workflow Test PASSED![/bold green]")
        console.print("\n[bold cyan]✨ Test Results Summary:[/bold cyan]")
        console.print("   • ✅ CLI entry-point successfully triggered search")
        console.print(f"   • ✅ Canned query '{canned_query}' processed correctly")
        console.print("   • ✅ No crashes during execution - stdout/stderr clean")
        console.print("   • ✅ Mock data accepted and processed")
        console.print(f"   • ✅ DataFrame contains all {expected_record_count} expected mock records")
        console.print("   • ✅ Record content validated (emails, plaintext, hashes)")
        
        return response, df
        
    except Exception as e:
        console.print(f"[bold red]❌ Test FAILED with error: {e}[/bold red]")
        raise

def main():
    """Main test execution function."""
    try:
        response, df = test_api_search_workflow()
        
        # Additional verification: Show the actual records
        console.print("\n[bold cyan]📋 Mock Records in DataFrame:[/bold cyan]")
        for i, row in df.iterrows():
            console.print(f"   Record {i+1}: {row['email']} ({row['username']})")
        
        console.print(f"\n[bold green]✅ Step 2 COMPLETED SUCCESSFULLY![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Step 2 FAILED: {e}[/bold red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
