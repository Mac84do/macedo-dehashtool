#!/usr/bin/env python3
"""
Test script to verify the PDF shows all records without truncation.
"""

import os
import pandas as pd
from datetime import datetime
from pdf_generator import generate_pdf_report
from rich.console import Console

console = Console()

def test_full_pdf_generation():
    """Test PDF generation with a large dataset to ensure no truncation."""
    
    console.print("[bold]Testing Full PDF Generation (No Truncation)[/bold]")
    
    # Create a larger dataset to test (more than 100 records)
    emails = [f"user{i}@example{i%10}.com" for i in range(150)]
    passwords = [f"password{i}" for i in range(150)]
    
    test_data = pd.DataFrame({
        'email': emails,
        'password': passwords
    })
    
    console.print(f"[cyan]Created test dataset with {len(test_data)} records[/cyan]")
    
    # Create test CSV file
    date_str = datetime.now().strftime('%Y-%m-%d')
    csv_filename = f"output/{date_str}_test_full_dataset.csv"
    
    try:
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
        
        # Save test data to CSV
        test_data.to_csv(csv_filename, index=False)
        console.print(f"[green]✅ Test CSV created: {csv_filename}[/green]")
        
        # Generate PDF
        pdf_path = generate_pdf_report(csv_filename)
        console.print(f"[green]✅ PDF generated: {pdf_path}[/green]")
        
        # Verify PDF file exists and has reasonable size
        if os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
            console.print(f"[green]✅ PDF file size: {pdf_size:,} bytes[/green]")
            
            # A PDF with 150 records should be significantly larger than one with 100
            if pdf_size > 50000:  # Expect at least 50KB for a full dataset
                console.print(f"[bold green]🎉 PDF appears to contain full dataset![/bold green]")
            else:
                console.print(f"[yellow]⚠️ PDF seems small - may still be truncated[/yellow]")
        else:
            console.print(f"[red]❌ PDF file not found after generation[/red]")
        
        console.print(f"[cyan]Test complete. Check the PDF manually to verify all {len(test_data)} records are included.[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")
        console.print(f"[red]Error type: {type(e).__name__}[/red]")
    
    finally:
        # Clean up (optional - comment out if you want to keep test files)
        # if os.path.exists(csv_filename):
        #     os.remove(csv_filename)
        # if os.path.exists(pdf_path):
        #     os.remove(pdf_path)
        pass

if __name__ == "__main__":
    test_full_pdf_generation()
