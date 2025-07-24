#!/usr/bin/env python3
"""
Test script that mimics exactly what main.py does for file saving.
"""

import os
import re
import pandas as pd
from datetime import datetime
from rich.console import Console

console = Console()

def test_exact_save_process():
    """Test the exact same process that main.py uses."""
    
    print("=== Testing Exact Main.py Save Process ===")
    
    # Create sample data (similar to what comes from API)
    df = pd.DataFrame({
        'email': ['test@example.com', 'user@test.com', 'admin@example.org'],
        'password': ['password123', 'secret456', 'admin2024']
    })
    
    # Simulate different search values that might cause issues
    test_searches = [
        "example.com",
        "test@domain.com",
        "domain with spaces.com",
        "special!@#$%^&*()chars.com",
        "icasa.org.za"  # The domain from your previous search
    ]
    
    for search_value in test_searches:
        console.print(f"\\n[bold]Testing search value: {search_value}[/bold]")
        
        # Get current date and time (same as main.py)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Create output directory if it doesn't exist (same as main.py)
        output_dir = 'output'
        try:
            os.makedirs(output_dir, exist_ok=True)
            console.print(f"[green]Using output directory: {os.path.abspath(output_dir)}[/green]")
        except PermissionError as e:
            console.print(f"[red]Permission denied creating directory: {os.path.abspath(output_dir)}[/red]")
            console.print(f"[red]Error details: {str(e)}[/red]")
            continue
        except Exception as e:
            console.print(f"[red]Unexpected error creating output directory: {str(e)}[/red]")
            continue
        
        # Create file name (same as main.py)
        query = re.sub(r'[^a-zA-Z0-9._-]', '_', search_value)
        file_name = f"{output_dir}/{date_str}_{query}.csv"
        
        # Save to CSV (same as main.py)
        console.print(f"[cyan]Attempting to save to: {file_name}[/cyan]")
        console.print(f"[cyan]File exists: {os.path.exists(file_name)}[/cyan]")
        
        try:
            # Check if file is locked by another process
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'a'):
                        pass
                    console.print(f"[cyan]File not locked, proceeding...[/cyan]")
                except PermissionError:
                    console.print(f"[yellow]File appears to be locked, will try to overwrite...[/yellow]")
            
            df.to_csv(file_name, index=False)
            console.print(f"[green]✅ Dataframe saved to {file_name}[/green]")
            
            # Clean up the test file
            os.remove(file_name)
            console.print(f"[cyan]Test file cleaned up[/cyan]")
            
        except PermissionError as e:
            console.print(f"[red]❌ Permission denied writing to {file_name}[/red]")
            console.print(f"[red]Error details: {str(e)}[/red]")
            console.print(f"[red]Errno: {e.errno}[/red]")
            
        except Exception as e:
            console.print(f"[red]❌ Unexpected error saving CSV: {str(e)}[/red]")
            console.print(f"[red]Error type: {type(e).__name__}[/red]")
    
    print("\\n=== Test Complete ===")

if __name__ == "__main__":
    test_exact_save_process()
