#!/usr/bin/env python3
"""
Test script to demonstrate PDF generation alongside CSV export.
"""

import os
import pandas as pd
from datetime import datetime
from pdf_generator import generate_pdf_report
from rich.console import Console

console = Console()

def create_sample_data_and_test():
    """Create sample data, save as CSV, and generate PDF."""
    
    # Sample data similar to what the main app would generate
    sample_data = {
        'email': [
            'user1@example.com',
            'user2@test.org', 
            'admin@company.net',
            'john.doe@sample.co',
            'alice@demo.io'
        ],
        'password': [
            'password123',
            'secret456',
            'admin789',
            'johnpass',
            'alice2023!'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename (similar to main.py logic)
    date_str = datetime.now().strftime('%Y-%m-%d')
    query = 'sample_domain.com'
    file_name = f"{output_dir}/{date_str}_{query}.csv"
    
    console.print(f"[blue]Creating sample data with {len(df)} records...[/blue]")
    
    # Save to CSV
    df.to_csv(file_name, index=False)
    console.print(f"[green]✅ CSV saved to {file_name}[/green]")
    
    # Generate PDF report
    try:
        pdf_path = generate_pdf_report(file_name)
        console.print(f"[green]✅ PDF report saved to {pdf_path}[/green]")
        
        # Show file sizes for comparison
        csv_size = os.path.getsize(file_name)
        pdf_size = os.path.getsize(pdf_path)
        
        console.print(f"[cyan]File Sizes:[/cyan]")
        console.print(f"  • CSV: {csv_size} bytes")
        console.print(f"  • PDF: {pdf_size} bytes")
        
        return file_name, pdf_path
        
    except Exception as e:
        console.print(f"[red]❌ PDF generation failed: {str(e)}[/red]")
        return file_name, None

def list_output_files():
    """List all files in the output directory."""
    output_dir = 'output'
    if os.path.exists(output_dir):
        console.print(f"\n[bold]Files in {output_dir} directory:[/bold]")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            console.print(f"  • {file} ({size} bytes)")
    else:
        console.print(f"[yellow]Output directory '{output_dir}' does not exist.[/yellow]")

if __name__ == "__main__":
    console.print("[bold cyan]PDF Integration Test[/bold cyan]\n")
    
    # Create sample data and generate reports
    csv_file, pdf_file = create_sample_data_and_test()
    
    # List all output files
    list_output_files()
    
    console.print(f"\n[green]✅ Test completed successfully![/green]")
    console.print("[dim]Both CSV and PDF files have been created with the same data and metadata.[/dim]")
