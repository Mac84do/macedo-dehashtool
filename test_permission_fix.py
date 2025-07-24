#!/usr/bin/env python3
"""
Test script to verify the automatic permission fix works.
"""

import os
import stat
import pandas as pd
from datetime import datetime
from rich.console import Console

console = Console()

def test_permission_fix():
    """Test the automatic permission fix."""
    
    console.print("[bold]Testing Automatic Permission Fix[/bold]")
    
    # Remove the output directory to test creation with proper permissions
    test_dir = 'test_output'
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    
    console.print(f"[cyan]Creating test directory: {test_dir}[/cyan]")
    
    # Create directory and set permissions (same logic as main.py)
    try:
        os.makedirs(test_dir, exist_ok=True)
        
        # On Windows, set full permissions to avoid Errno 13 issues
        if os.name == 'nt':  # Windows
            try:
                os.chmod(test_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                console.print(f"[green]✅ Set full permissions on {test_dir}[/green]")
            except Exception as chmod_e:
                console.print(f"[yellow]⚠️ Could not set directory permissions: {chmod_e}[/yellow]")
        
        console.print(f"[green]✅ Directory created: {os.path.abspath(test_dir)}[/green]")
        
        # Test file creation
        test_data = pd.DataFrame({
            'email': ['test@example.com'],
            'password': ['test123']
        })
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        test_file = f"{test_dir}/{date_str}_test.csv"
        
        console.print(f"[cyan]Testing file creation: {test_file}[/cyan]")
        
        test_data.to_csv(test_file, index=False)
        console.print(f"[green]✅ File created successfully[/green]")
        
        # Verify file exists and has content
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            console.print(f"[green]✅ File verified: {file_size} bytes[/green]")
        else:
            console.print(f"[red]❌ File not found after creation[/red]")
        
        # Clean up
        import shutil
        shutil.rmtree(test_dir)
        console.print(f"[cyan]Test directory cleaned up[/cyan]")
        
        console.print(f"[bold green]🎉 Permission fix test PASSED![/bold green]")
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")
        console.print(f"[red]Error type: {type(e).__name__}[/red]")

if __name__ == "__main__":
    test_permission_fix()
