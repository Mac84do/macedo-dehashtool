#!/usr/bin/env python3
"""
Step 2 Additional Test: Email Query Test

Test the API search workflow with an email query to demonstrate 
complete coverage of both domain and email search types.
"""

import sys
import json
import configparser
from unittest.mock import patch
from rich.console import Console
from rich.panel import Panel

# Import our modules
from dehashed import search
from result_extraction_v2 import extract_all_fields

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
def test_email_query_search(mock_post):
    """Test the API search workflow with an email query."""
    
    console.print(Panel.fit(
        "[bold cyan]📧 Step 2: Email Query Test[/bold cyan]\n"
        "Testing API search with email query:\n"
        "• Email query processing\n"
        "• Mock data acceptance\n"
        "• Stdout/stderr capture validation",
        title="Email Query Test"
    ))
    
    # Load credentials and mock data
    email, api_key = load_test_config()
    mock_response = load_mock_response()
    
    # Configure mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.headers = {
        'x-ratelimit-remaining': '94',
        'x-ratelimit-limit': '100'
    }
    
    # Test with email query (should not be formatted with domain: prefix)
    canned_email_query = "admin@testdomain.org"
    console.print(f"[cyan]🔍 Canned email query:[/cyan] {canned_email_query}")
    
    try:
        # Trigger the search with email query
        response = search(query=canned_email_query, email=email, api_key=api_key)
        console.print("[green]✅ Email query search completed without crash[/green]")
        
        # Verify mock was called
        assert mock_post.called, "Mock should have been called"
        
        # Check that the email query was NOT formatted with domain: prefix
        # (unlike domain queries which get the domain: prefix)
        call_args = mock_post.call_args
        payload = call_args[1]['json']  # Get the JSON payload sent to the API
        assert payload['query'] == canned_email_query, f"Expected query '{canned_email_query}', got '{payload['query']}'"
        console.print("[green]✅ Email query processed correctly (no domain: prefix added)[/green]")
        
        # Extract and validate data
        df = extract_all_fields(response)
        assert len(df) == 4, f"Expected 4 records, got {len(df)}"
        console.print(f"[green]✅ DataFrame contains {len(df)} mock records[/green]")
        
        console.print("[bold green]🎉 Email Query Test PASSED![/bold green]")
        return response, df
        
    except Exception as e:
        console.print(f"[bold red]❌ Email Query Test FAILED: {e}[/bold red]")
        raise

def main():
    """Main test execution."""
    try:
        response, df = test_email_query_search()
        console.print("\n[bold green]✅ Email Query Test Completed Successfully![/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Test Failed: {e}[/bold red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
