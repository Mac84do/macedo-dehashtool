#!/usr/bin/env python3
"""
Dry-run demonstration script for Dehashed API tool.

This script demonstrates the full functionality of the tool without requiring
a real API key by using mocked API responses. It shows:

1. API key handling (mocked)
2. Search functionality with rate-limit simulation
3. Data extraction and processing
4. CSV and PDF generation
5. Rich formatted output

Usage:
    python dry_run_demo.py
"""

import os
import sys
import tempfile
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

# Import our modules
from get_api_key import get_api_key
from dehashed import search, DeHashedRateLimitError, DeHashedAPIError
from result_extraction import extract_email_password_data, print_extraction_summary, print_dataframe_table
from pdf_generator import generate_pdf_report

console = Console()

# Sample mock data for different scenarios
MOCK_RESPONSES = {
    'example.com': {
        'success': True,
        'total': 5,
        'entries': [
            {
                'id': '1',
                'email': 'john.doe@example.com',
                'password': 'password123',
                'username': 'john.doe',
                'domain': 'example.com',
                'database_name': 'Example Corp Breach 2023'
            },
            {
                'id': '2',
                'email': 'jane.smith@example.com',
                'password': 'mySecretPass!',
                'username': 'jane.smith',
                'domain': 'example.com',
                'database_name': 'Example Corp Breach 2023'
            },
            {
                'id': '3',
                'email': 'admin@example.com',
                'password': 'admin123',
                'username': 'admin',
                'domain': 'example.com',
                'database_name': 'Example Corp Breach 2023'
            },
            {
                'id': '4',
                'email': 'user@example.com',
                'password': '',  # Empty password - will be filtered out
                'username': 'user',
                'domain': 'example.com',
                'database_name': 'Example Corp Breach 2023'
            },
            {
                'id': '5',
                'email': 'test@example.com',
                'password': 'testpass456',
                'username': 'test',
                'domain': 'example.com',
                'database_name': 'Example Corp Breach 2023'
            }
        ]
    },
    'testcompany.org': {
        'success': True,
        'total': 3,
        'entries': [
            {
                'id': '6',
                'email': 'employee1@testcompany.org',
                'password': 'work123',
                'username': 'employee1',
                'domain': 'testcompany.org',
                'database_name': 'Test Company DB Leak 2022'
            },
            {
                'id': '7',
                'email': 'manager@testcompany.org',
                'password': 'manager2023!',
                'username': 'manager',
                'domain': 'testcompany.org',
                'database_name': 'Test Company DB Leak 2022'
            },
            {
                'id': '8',
                'email': 'hr@testcompany.org',
                'password': 'humanresources',
                'username': 'hr',
                'domain': 'testcompany.org',
                'database_name': 'Test Company DB Leak 2022'
            }
        ]
    },
    'user@demo.com': {
        'success': True,
        'total': 1,
        'entries': [
            {
                'id': '9',
                'email': 'user@demo.com',
                'password': 'demoPassword123',
                'username': 'user',
                'domain': 'demo.com',
                'database_name': 'Demo Site Breach 2024'
            }
        ]
    }
}

def mock_search_function(query, api_key, max_retries=3):
    """
    Mock search function that simulates API behavior without real requests.
    
    Args:
        query: Search query
        api_key: API key (ignored in mock)
        max_retries: Max retries (ignored in mock)
    
    Returns:
        Mock API response based on query
    """
    # Simulate rate limiting for certain queries
    if query == 'ratelimit.com':
        raise DeHashedRateLimitError("Rate limit exceeded in demo (simulated)")
    
    # Simulate API error for certain queries
    if query == 'error.com':
        raise DeHashedAPIError("API error in demo (simulated)")
    
    # Return mock data if available
    if query in MOCK_RESPONSES:
        return MOCK_RESPONSES[query]
    
    # Default response for unknown queries
    return {
        'success': True,
        'total': 0,
        'entries': []
    }

def print_demo_banner():
    """Print a banner explaining this is a demo."""
    title = Text("Dehashed API Tool - DRY RUN DEMO", style="bold cyan")
    banner_text = Text.assemble(
        "This is a ", ("dry-run demonstration", "bold yellow"), " of the Dehashed API tool.\\n",
        "All API responses are ", ("mocked", "bold red"), " and no real API calls are made.\\n",
        "No real API key is required for this demonstration.\\n\\n",
        "Available demo queries:\\n",
        "• ", ("example.com", "green"), " - Returns 5 sample records\\n",
        "• ", ("testcompany.org", "green"), " - Returns 3 sample records\\n",
        "• ", ("user@demo.com", "green"), " - Returns 1 sample record\\n",
        "• ", ("ratelimit.com", "yellow"), " - Simulates rate limiting\\n",
        "• ", ("error.com", "red"), " - Simulates API error\\n",
        "• Any other query - Returns empty results"
    )
    
    banner = Panel(
        banner_text,
        title=title,
        border_style="yellow",
        padding=(1, 2)
    )
    
    console.print(banner)
    console.print()

def demonstrate_api_key_handling():
    """Demonstrate API key handling."""
    console.print("[bold blue]📋 Step 1: API Key Handling Demo[/bold blue]")
    
    # Mock getting API key
    with patch('get_api_key.os.getenv', return_value='demo_api_key_12345'):
        api_key = get_api_key()
        if api_key:
            console.print(f"[green]✅ Mock API key loaded: {api_key[:10]}...[/green]")
        else:
            console.print("[yellow]⚠️  No API key found (this is normal for demo)[/yellow]")
    
    console.print()

def demonstrate_search_functionality():
    """Demonstrate search functionality with various scenarios."""
    console.print("[bold blue]🔍 Step 2: Search Functionality Demo[/bold blue]")
    
    # Get user choice for demo query
    console.print("Choose a demo scenario:")
    console.print("1) example.com (5 records)")
    console.print("2) testcompany.org (3 records)") 
    console.print("3) user@demo.com (1 record)")
    console.print("4) ratelimit.com (rate limit demo)")
    console.print("5) error.com (error handling demo)")
    console.print("6) Custom query (empty results)")
    
    try:
        choice = Prompt.ask("Select scenario", choices=["1", "2", "3", "4", "5", "6"], default="1")
    except EOFError:
        # Handle automated input
        choice = "1"
        console.print("[dim]Using default scenario 1 (example.com)[/dim]")
    
    # Map choices to queries
    if choice == "6":
        try:
            custom_query = Prompt.ask("Enter custom query")
        except EOFError:
            custom_query = "testquery.com"
            console.print("[dim]Using default custom query (testquery.com)[/dim]")
        query_map = {
            "1": "example.com",
            "2": "testcompany.org", 
            "3": "user@demo.com",
            "4": "ratelimit.com",
            "5": "error.com",
            "6": custom_query
        }
    else:
        query_map = {
            "1": "example.com",
            "2": "testcompany.org", 
            "3": "user@demo.com",
            "4": "ratelimit.com",
            "5": "error.com",
            "6": "testquery.com"
        }
    
    query = query_map[choice]
    console.print(f"\\n[cyan]Searching for: {query}[/cyan]")
    
    # Perform mock search
    try:
        with patch('dehashed.requests.post') as mock_post:
            # Configure mock response based on query
            if query in MOCK_RESPONSES:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = MOCK_RESPONSES[query]
                mock_post.return_value = mock_response
                
                response = search(query=query, api_key='demo_key')
                console.print("[green]✅ Mock API search completed[/green]")
                return response, query
            
            elif query == 'ratelimit.com':
                # Simulate rate limiting
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_response.headers = {'Retry-After': '2'}
                mock_post.return_value = mock_response
                
                try:
                    search(query=query, api_key='demo_key', max_retries=0)
                except DeHashedRateLimitError as e:
                    console.print(f"[yellow]⚠️  Rate limit demo: {e}[/yellow]")
                    return None, query
            
            elif query == 'error.com':
                # Simulate API error
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.json.return_value = {'error': 'Unauthorized (demo)'}
                mock_post.return_value = mock_response
                
                try:
                    search(query=query, api_key='demo_key')
                except DeHashedAPIError as e:
                    console.print(f"[red]❌ API error demo: {e}[/red]")
                    return None, query
            
            else:
                # Empty results for unknown queries
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'success': True, 'total': 0, 'entries': []}
                mock_post.return_value = mock_response
                
                response = search(query=query, api_key='demo_key')
                console.print("[green]✅ Mock API search completed (no results)[/green]")
                return response, query
                
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        return None, query

def demonstrate_data_processing(response, query):
    """Demonstrate data extraction and processing."""
    if not response:
        return None
        
    console.print("\\n[bold blue]📊 Step 3: Data Processing Demo[/bold blue]")
    
    # Extract data
    original_count = len(response.get('entries', []))
    df = extract_email_password_data(response)
    
    # Print extraction summary
    print_extraction_summary(df, original_count)
    
    # Display results if any
    if len(df) > 0:
        print_dataframe_table(df)
        return df
    else:
        console.print("[yellow]No valid email/password pairs found[/yellow]")
        return None

def demonstrate_file_export(df, query):
    """Demonstrate CSV and PDF export functionality."""
    if df is None or len(df) == 0:
        return None, None
        
    console.print("\\n[bold blue]💾 Step 4: File Export Demo[/bold blue]")
    
    # Create temporary directory for demo files
    temp_dir = tempfile.mkdtemp()
    
    # Generate filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    safe_query = query.replace('@', '_at_').replace('.', '_')
    csv_file = os.path.join(temp_dir, f"{date_str}_{safe_query}_demo.csv")
    
    # Save to CSV
    df.to_csv(csv_file, index=False)
    console.print(f"[green]✅ Demo CSV saved to: {csv_file}[/green]")
    
    # Generate PDF
    try:
        pdf_file = generate_pdf_report(csv_file)
        console.print(f"[green]✅ Demo PDF saved to: {pdf_file}[/green]")
        
        # Show file sizes
        csv_size = os.path.getsize(csv_file)
        pdf_size = os.path.getsize(pdf_file)
        
        console.print(f"\\n[cyan]File Information:[/cyan]")
        console.print(f"  • CSV: {csv_size} bytes")
        console.print(f"  • PDF: {pdf_size} bytes")
        
        return csv_file, pdf_file
        
    except Exception as e:
        console.print(f"[yellow]⚠️  PDF generation failed: {e}[/yellow]")
        return csv_file, None

def main():
    """Main demo function."""
    try:
        # Print demo banner
        print_demo_banner()
        
        # Step 1: API Key handling
        demonstrate_api_key_handling()
        
        # Step 2: Search functionality
        response, query = demonstrate_search_functionality()
        
        # Step 3: Data processing
        df = demonstrate_data_processing(response, query)
        
        # Step 4: File export
        csv_file, pdf_file = demonstrate_file_export(df, query)
        
        # Summary
        console.print("\\n[bold green]🎉 Dry-Run Demo Completed![/bold green]")
        console.print("\\n[dim]This demonstration showed all major features:")
        console.print("• API key handling (mocked)")
        console.print("• Search functionality with error handling")
        console.print("• Data extraction and filtering")
        console.print("• CSV and PDF export")
        console.print("• Rich formatted output")
        
        if csv_file or pdf_file:
            console.print(f"\\n[yellow]Demo files created (you can delete them when done):[/yellow]")
            if csv_file:
                console.print(f"  • CSV: {csv_file}")
            if pdf_file:
                console.print(f"  • PDF: {pdf_file}")
        
        console.print("\\n[dim]To use with real data, set up your API key and run main.py[/dim]")
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]Demo cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\\n[red]Demo failed: {e}[/red]")

if __name__ == "__main__":
    main()
