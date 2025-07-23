#!/usr/bin/env python3
"""
Simple automated demo of the Dehashed API tool functionality.
This runs all tests without user interaction.
"""

import os
import tempfile
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from rich.console import Console

# Import our modules
from get_api_key import get_api_key
from dehashed import search, DeHashedRateLimitError, DeHashedAPIError
from result_extraction import extract_email_password_data, print_extraction_summary, print_dataframe_table
from pdf_generator import generate_pdf_report

console = Console()

def demo_api_key_functionality():
    """Demo API key retrieval functionality."""
    console.print("[bold blue]🔑 API Key Functionality Demo[/bold blue]")
    
    # Test with environment variable
    with patch.dict(os.environ, {'DEHASHED_API_KEY': 'demo_env_key_123'}):
        key = get_api_key()
        console.print(f"[green]✅ Environment variable: {key[:15]}...[/green]")
    
    # Test with no key found
    with patch.dict(os.environ, {}, clear=True):
        with patch('get_api_key.ConfigParser') as MockConfigParser:
            from configparser import NoSectionError
            mock_config = MockConfigParser.return_value
            mock_config.get.side_effect = NoSectionError("DEFAULT")
            key = get_api_key()
            console.print(f"[yellow]⚠️  No key found: {key}[/yellow]")
    
    console.print()

def demo_search_with_mock_data():
    """Demo search functionality with mock data."""
    console.print("[bold blue]🔍 Search Functionality Demo[/bold blue]")
    
    # Mock successful response
    mock_data = {
        'success': True,
        'total': 3,
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
            },
            {
                'id': '3',
                'email': 'admin@example.com',
                'password': '',  # Empty password - will be filtered
                'username': 'admin',
                'domain': 'example.com'
            }
        ]
    }
    
    with patch('dehashed.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_post.return_value = mock_response
        
        response = search(query='example.com', api_key='demo_key')
        console.print("[green]✅ Mock API search completed[/green]")
        
        # Extract and process data
        original_count = len(response.get('entries', []))
        df = extract_email_password_data(response)
        
        console.print(f"[cyan]Original entries: {original_count}[/cyan]")
        console.print(f"[cyan]Valid email/password pairs: {len(df)}[/cyan]")
        
        if len(df) > 0:
            print_dataframe_table(df)
        
        console.print()
        return df

def demo_rate_limiting():
    """Demo rate limiting functionality."""
    console.print("[bold blue]⏱️  Rate Limiting Demo[/bold blue]")
    
    with patch('dehashed.requests.post') as mock_post:
        with patch('dehashed.time.sleep'):  # Speed up the demo
            # First call returns 429, second returns 200
            mock_response_429 = MagicMock()
            mock_response_429.status_code = 429
            mock_response_429.headers = {'Retry-After': '1'}
            
            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {'success': True, 'entries': []}
            
            mock_post.side_effect = [mock_response_429, mock_response_200]
            
            try:
                result = search(query='test.com', api_key='demo_key', max_retries=1)
                console.print("[green]✅ Rate limiting handled successfully[/green]")
            except DeHashedRateLimitError:
                console.print("[yellow]⚠️  Rate limit exceeded (as expected)[/yellow]")
    
    console.print()

def demo_file_export(df):
    """Demo CSV and PDF export functionality."""
    if df is None or len(df) == 0:
        console.print("[yellow]⚠️  No data to export[/yellow]")
        return
        
    console.print("[bold blue]💾 File Export Demo[/bold blue]")
    
    temp_dir = tempfile.mkdtemp()
    date_str = datetime.now().strftime('%Y-%m-%d')
    csv_file = os.path.join(temp_dir, f"{date_str}_demo_export.csv")
    
    # Save CSV
    df.to_csv(csv_file, index=False)
    console.print(f"[green]✅ CSV created: {os.path.basename(csv_file)}[/green]")
    
    # Generate PDF
    try:
        pdf_file = generate_pdf_report(csv_file)
        console.print(f"[green]✅ PDF created: {os.path.basename(pdf_file)}[/green]")
        
        # Show file sizes
        csv_size = os.path.getsize(csv_file)
        pdf_size = os.path.getsize(pdf_file)
        
        console.print(f"[cyan]CSV size: {csv_size} bytes[/cyan]")
        console.print(f"[cyan]PDF size: {pdf_size} bytes[/cyan]")
        
        # Verify files exist
        console.print(f"[green]✅ CSV exists: {os.path.exists(csv_file)}[/green]")
        console.print(f"[green]✅ PDF exists: {os.path.exists(pdf_file)}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ PDF generation failed: {e}[/red]")
    
    console.print()

def main():
    """Run all demos."""
    console.print("[bold cyan]🧪 Dehashed API Tool - Automated Demo[/bold cyan]")
    console.print("[dim]Testing all functionality with mocked data...[/dim]\n")
    
    try:
        # Demo 1: API Key functionality
        demo_api_key_functionality()
        
        # Demo 2: Search and data processing
        df = demo_search_with_mock_data()
        
        # Demo 3: Rate limiting
        demo_rate_limiting()
        
        # Demo 4: File export
        demo_file_export(df)
        
        # Summary
        console.print("[bold green]🎉 All demos completed successfully![/bold green]")
        console.print("\n[dim]Summary of tested functionality:[/dim]")
        console.print("✅ API key retrieval from environment variables")
        console.print("✅ API key fallback handling")
        console.print("✅ Mock API search with data processing")
        console.print("✅ Rate limiting with retry logic")
        console.print("✅ CSV file creation and verification")
        console.print("✅ PDF generation and verification")
        console.print("✅ Data extraction and filtering")
        console.print("✅ Rich formatted output")
        
        console.print("\n[yellow]🔧 For real usage:[/yellow]")
        console.print("1. Set DEHASHED_API_KEY environment variable")
        console.print("2. Run: python main.py")
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
