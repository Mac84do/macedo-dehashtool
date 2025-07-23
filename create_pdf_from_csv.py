#!/usr/bin/env python3
"""
Utility script to generate PDF reports from existing CSV files.

This can be used to create PDF reports from CSV files that were generated
without PDF reports, or to regenerate PDF reports.
"""

import sys
import os
import argparse
from pdf_generator import generate_pdf_report
from rich.console import Console

console = Console()

def main():
    """Main function to handle command line arguments and generate PDFs."""
    parser = argparse.ArgumentParser(
        description="Generate PDF reports from CSV files",
        epilog="Example: python create_pdf_from_csv.py output/2025-01-23_example.com.csv"
    )
    
    parser.add_argument(
        'csv_files',
        nargs='*',
        help='Path(s) to CSV file(s) to convert to PDF (not needed with --batch)'
    )
    
    parser.add_argument(
        '--output-dir',
        '-o',
        help='Custom output directory for PDF files (default: same as CSV)'
    )
    
    parser.add_argument(
        '--batch',
        '-b',
        action='store_true',
        help='Process all CSV files in the output directory'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch and not args.csv_files:
        console.print("[red]❌ Error: Must provide CSV files or use --batch mode.[/red]")
        parser.print_help()
        sys.exit(1)
    
    csv_files = []
    
    # Handle batch processing
    if args.batch:
        output_dir = args.output_dir or 'output'
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(output_dir, file))
            console.print(f"[blue]Found {len(csv_files)} CSV files in {output_dir}[/blue]")
        else:
            console.print(f"[red]❌ Output directory '{output_dir}' does not exist.[/red]")
            sys.exit(1)
    else:
        csv_files = args.csv_files
    
    if not csv_files:
        console.print("[yellow]⚠️  No CSV files to process.[/yellow]")
        sys.exit(0)
    
    # Process each CSV file
    success_count = 0
    error_count = 0
    
    console.print(f"[blue]Processing {len(csv_files)} CSV file(s)...[/blue]\\n")
    
    for csv_file in csv_files:
        try:
            # Check if file exists
            if not os.path.exists(csv_file):
                console.print(f"[red]❌ File not found: {csv_file}[/red]")
                error_count += 1
                continue
            
            # Check if it's a CSV file
            if not csv_file.endswith('.csv'):
                console.print(f"[yellow]⚠️  Skipping non-CSV file: {csv_file}[/yellow]")
                continue
            
            # Generate PDF
            console.print(f"[cyan]Processing: {os.path.basename(csv_file)}[/cyan]")
            
            # Handle custom output directory
            if args.output_dir:
                csv_basename = os.path.splitext(os.path.basename(csv_file))[0]
                custom_pdf_path = os.path.join(args.output_dir, f"{csv_basename}.pdf")
                
                # Ensure output directory exists
                os.makedirs(args.output_dir, exist_ok=True)
                
                # Generate PDF with custom path
                from pdf_generator import create_pdf_from_csv
                pdf_path = create_pdf_from_csv(csv_file, custom_pdf_path)
            else:
                pdf_path = generate_pdf_report(csv_file)
            
            console.print(f"  [green]✅ Created: {os.path.basename(pdf_path)}[/green]")
            success_count += 1
            
        except Exception as e:
            console.print(f"  [red]❌ Error: {str(e)}[/red]")
            error_count += 1
        
        console.print()  # Add spacing between files
    
    # Print summary
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  • [green]Successfully processed: {success_count}[/green]")
    if error_count > 0:
        console.print(f"  • [red]Errors: {error_count}[/red]")
    
    if success_count > 0:
        console.print(f"\\n[green]✅ PDF generation completed![/green]")
    else:
        console.print(f"\\n[red]❌ No PDFs were generated.[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)
