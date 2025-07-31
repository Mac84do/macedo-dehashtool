#!/usr/bin/env python3
"""
Test runner script to demonstrate the test fixtures and mock environment.

This script demonstrates:
1. Loading dummy config.ini with fake credentials
2. Using mock JSON response from DeHashed v2 API
3. Testing both plaintext-only and hash-only record handling
4. Mocking network requests to avoid hitting real API
"""

import json
import configparser
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import our modules
from dehashed import search
from result_extraction_v2 import extract_all_fields, list_hash_columns

console = Console()

def load_test_config():
    """Load the test configuration with fake credentials."""
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    
    email = config.get('DEFAULT', 'DEHASHED_EMAIL')
    api_key = config.get('DEFAULT', 'DEHASHED_API_KEY')
    
    console.print(f"[yellow]📧 Test Email:[/yellow] {email}")
    console.print(f"[yellow]🔑 Test API Key:[/yellow] {api_key[:20]}...")
    
    return email, api_key

def load_mock_response():
    """Load the mock DeHashed response from JSON file."""
    with open('test_fixtures/mock_dehashed_response.json', 'r') as f:
        mock_response = json.load(f)
    
    console.print(f"[cyan]📋 Mock Response loaded:[/cyan]")
    console.print(f"   • Total entries: {mock_response['total']}")
    console.print(f"   • Balance: {mock_response['balance']} credits")
    console.print(f"   • Success: {mock_response['success']}")
    
    return mock_response

def demonstrate_plaintext_vs_hash_records(mock_response):
    """Demonstrate the handling of plaintext vs hash-only records."""
    console.print("\n[bold cyan]🔍 Analyzing Record Types:[/bold cyan]")
    
    # Create a table to show the records
    table = Table(title="Mock DeHashed Records Analysis")
    table.add_column("ID", style="cyan")
    table.add_column("Email", style="green")
    table.add_column("Username", style="yellow")
    table.add_column("Password Type", style="magenta")
    table.add_column("Password/Hash", style="red")
    
    for entry in mock_response['entries']:
        if entry.get('password') and entry['password'].strip():
            password_type = "Plaintext"
            password_value = entry['password'][:20] + "..." if len(entry['password']) > 20 else entry['password']
        elif entry.get('hash') or entry.get('hashed_password'):
            password_type = "Hash Only"
            hash_value = entry.get('hash') or entry.get('hashed_password')
            password_value = hash_value[:20] + "..." if len(hash_value) > 20 else hash_value
        else:
            password_type = "None"
            password_value = "N/A"
        
        table.add_row(
            entry['id'],
            entry['email'],
            entry['username'],
            password_type,
            password_value
        )
    
    console.print(table)

@patch('requests.post')
def test_mocked_api_call(mock_post):
    """Test the mocked API call to demonstrate network interception."""
    console.print("\n[bold cyan]🌐 Testing Mocked API Call:[/bold cyan]")
    
    # Load test fixtures
    email, api_key = load_test_config()
    mock_response = load_mock_response()
    
    # Configure the mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.headers = {
        'x-ratelimit-remaining': '95',
        'x-ratelimit-limit': '100'
    }
    
    # Make the "API call" using our mocked function
    response = search('example.com', email, api_key)
    
    # Verify the mock was called
    assert mock_post.called, "Mock should have been called"
    console.print("[green]✅ Mock API call intercepted successfully![/green]")
    
    # Show that we got the expected response
    console.print(f"[cyan]📊 Response received:[/cyan]")
    console.print(f"   • Entries: {len(response['entries'])}")
    console.print(f"   • Balance: {response['balance']}")
    
    return response

def test_data_extraction():
    """Test data extraction with both plaintext and hash records."""
    console.print("\n[bold cyan]🔧 Testing Data Extraction:[/bold cyan]")
    
    mock_response = load_mock_response()
    
    # Extract all fields from the mock response
    df = extract_all_fields(mock_response)
    
    console.print(f"[green]✅ Extracted {len(df)} records[/green]")
    console.print(f"[cyan]📋 Columns found:[/cyan] {', '.join(df.columns.tolist())}")
    
    # Test hash column detection
    hash_columns = list_hash_columns(df)
    console.print(f"[yellow]🔐 Hash columns detected:[/yellow] {', '.join(hash_columns)}")
    
    # Show plaintext vs hashed records
    plaintext_records = df[df['password'].notna() & (df['password'] != '')].shape[0]
    hash_records = len(df) - plaintext_records
    
    console.print(f"[green]📝 Plaintext records:[/green] {plaintext_records}")
    console.print(f"[red]🔐 Hash-only records:[/red] {hash_records}")
    
    return df

def main():
    """Main demonstration function."""
    console.print(Panel.fit(
        "[bold cyan]🧪 DeHashed Tool Test Fixtures Demonstration[/bold cyan]\n"
        "This script demonstrates the test environment setup:\n"
        "• Dummy config.ini with fake credentials\n"
        "• Mock JSON response with mixed record types\n"
        "• Network request interception using unittest.mock\n"
        "• Testing both plaintext and hash-only records",
        title="Test Fixtures Demo"
    ))
    
    try:
        # Load and show test config
        console.print("\n[bold yellow]1. Loading Test Configuration[/bold yellow]")
        email, api_key = load_test_config()
        
        # Load and analyze mock response
        console.print("\n[bold yellow]2. Loading Mock Response[/bold yellow]")
        mock_response = load_mock_response()
        demonstrate_plaintext_vs_hash_records(mock_response)
        
        # Test mocked API call
        console.print("\n[bold yellow]3. Testing Mocked API Call[/bold yellow]")
        response = test_mocked_api_call()
        
        # Test data extraction
        console.print("\n[bold yellow]4. Testing Data Extraction[/bold yellow]")
        df = test_data_extraction()
        
        console.print("\n[bold green]🎉 All test fixtures working correctly![/bold green]")
        console.print("\n[bold cyan]✨ Test Environment Summary:[/bold cyan]")
        console.print("   • ✅ Dummy config.ini loaded with fake credentials")
        console.print("   • ✅ Mock JSON response loaded with 4 test records")
        console.print("   • ✅ Network requests successfully intercepted")
        console.print("   • ✅ Both plaintext and hash-only records handled")
        console.print("   • ✅ Data extraction working with mixed record types")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during demonstration: {e}[/bold red]")
        raise

if __name__ == '__main__':
    main()
