#!/usr/bin/env python3
"""
Test script to check what headers the DeHashed API returns.
"""

from get_api_key import get_api_credentials
from dehashed import search
from rich.console import Console

console = Console()

def test_api_headers():
    """Test what headers the DeHashed API returns."""
    
    console.print("[bold]Testing DeHashed API Headers[/bold]")
    
    # Get API credentials
    email, api_key = get_api_credentials()
    if not email or not api_key:
        console.print("[red]❌ Missing API credentials![/red]")
        return
    
    console.print("[green]✅ API credentials loaded[/green]")
    
    try:
        # Make a simple API call to see headers
        console.print("[yellow]Making test API call to examine headers...[/yellow]")
        response = search("test.com", email, api_key)
        
        console.print("[green]✅ API call successful![/green]")
        console.print(f"[cyan]Found {len(response.get('entries', []))} entries[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ API call failed: {str(e)}[/red]")

if __name__ == "__main__":
    test_api_headers()
