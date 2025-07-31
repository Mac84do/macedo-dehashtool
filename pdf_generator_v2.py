#!/usr/bin/env python3
"""
PDF generator module for Dehashed API results (v2) - Enhanced Multi-Column PDF Generator.

This module provides functionality to create comprehensive PDF reports from CSV data
using ReportLab, including:
- Auto-sizing pages (landscape if many columns)
- ReportLab Table with alternating row colors
- Cover page with search metadata (query, datetime, API totals)
- Extraction summary embedding
- Hash-cracking results integration (step 6)
- Generated PDF path return
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from rich.console import Console

console = Console()


def auto_size_page_orientation(num_columns: int) -> tuple:
    """
    Determine optimal page size and orientation based on number of columns.
    
    Args:
        num_columns: Number of columns in the data
        
    Returns:
        tuple: (pagesize, is_landscape)
    """
    # Use landscape if we have more than 4 columns to fit more data
    if num_columns > 4:
        return landscape(A4), True
    else:
        return A4, False


def extract_metadata_from_filename_v2(csv_filename: str) -> dict:
    """
    Extract metadata from CSV filename (v2).
    Expected format: YYYY-MM-DD_query.csv
    
    Args:
        csv_filename: Path to the CSV file
        
    Returns:
        dict: Metadata including date, query, and filename
    """
    basename = os.path.basename(csv_filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Try to split by underscore to get date and query
    parts = name_without_ext.split('_', 1)
    
    if len(parts) >= 2:
        date_str = parts[0]
        query_str = parts[1].replace('_', ' ')  # Replace underscores back to spaces/special chars
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
        query_str = name_without_ext
    
    return {
        'date': date_str,
        'query': query_str,
        'filename': basename
    }


def create_pdf_from_dataframe_v2(
    df: pd.DataFrame, 
    query: str = "", 
    api_totals: Dict[str, Any] = None,
    extraction_summary: Dict[str, Any] = None,
    hash_crack_results: Dict[str, Any] = None,
    output_pdf_path: Optional[str] = None
) -> str:
    """
    Create a comprehensive PDF report from DataFrame with enhanced features (v2).
    
    Args:
        df: DataFrame containing the data to export
        query: The search query used
        api_totals: Dictionary containing API response totals
        extraction_summary: Dictionary containing extraction summary info
        hash_crack_results: Dictionary containing hash cracking results (step 6)
        output_pdf_path: Optional custom output path for PDF
        
    Returns:
        str: Path to the created PDF file
    """
    if output_pdf_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_pdf_path = f"dehashed_report_{timestamp}.pdf"
    
    # Determine page orientation based on number of columns
    pagesize, is_landscape = auto_size_page_orientation(len(df.columns))
    
    # Adjust margins for landscape
    if is_landscape:
        margins = {'rightMargin': 24, 'leftMargin': 24, 'topMargin': 48, 'bottomMargin': 24}
    else:
        margins = {'rightMargin': 36, 'leftMargin': 36, 'topMargin': 72, 'bottomMargin': 36}
    
    try:
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=pagesize,
            **margins
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.navy
        )
        
        # COVER PAGE
        title = Paragraph("Dehashed API Search Results Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Cover page metadata
        cover_data = [
            ['Search Query:', query or 'N/A'],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Records:', str(len(df))],
            ['Columns:', str(len(df.columns))],
            ['Page Orientation:', 'Landscape' if is_landscape else 'Portrait']
        ]
        
        if api_totals:
            cover_data.extend([
                ['API Total:', str(api_totals.get('total', 'N/A'))],
                ['API Success:', str(api_totals.get('success', 'N/A'))]
            ])
        
        cover_table = Table(cover_data, colWidths=[2.5*inch, 4*inch])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(cover_table)
        
        # Add extraction summary if provided
        if extraction_summary:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Extraction Summary", heading_style))
            
            summary_data = []
            for key, value in extraction_summary.items():
                summary_data.append([str(key).replace('_', ' ').title() + ':', str(value)])
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(summary_table)
        
        # Add hash cracking results if provided
        if hash_crack_results:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Hash Cracking Results", heading_style))
            
            crack_data = []
            for key, value in hash_crack_results.items():
                crack_data.append([str(key).replace('_', ' ').title() + ':', str(value)])
            
            crack_table = Table(crack_data, colWidths=[2.5*inch, 4*inch])
            crack_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(crack_table)
        
        elements.append(PageBreak())
        
        # DATA SECTION
        if len(df) > 0:
            elements.append(Paragraph("Extracted Data", heading_style))
            elements.append(Spacer(1, 12))
            
            # Prepare table data with all columns
            table_data = [list(df.columns)]  # Header row
            
            # Add all data rows
            for _, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    value = str(row[col]) if pd.notna(row[col]) else ''
                    # Truncate long values for display
                    if len(value) > 50:
                        value = value[:47] + '...'
                    row_data.append(value)
                table_data.append(row_data)
            
            # Calculate column widths based on page orientation
            if is_landscape:
                available_width = 10.5 * inch  # Landscape A4 minus margins
            else:
                available_width = 7.5 * inch   # Portrait A4 minus margins
            
            col_width = available_width / len(df.columns)
            col_widths = [col_width] * len(df.columns)
            
            # Create table
            data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Table style with alternating row colors
            table_style = [
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            
            # Apply alternating row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
                else:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
            
            data_table.setStyle(TableStyle(table_style))
            elements.append(data_table)
        else:
            elements.append(Paragraph("No data records found.", styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 20))
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total records: {len(df)}"
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        return output_pdf_path
        
    except Exception as e:
        raise Exception(f"Failed to create PDF: {str(e)}")


def create_pdf_from_csv_v2(csv_file_path: str, output_pdf_path: Optional[str] = None) -> str:
    """
    Create a PDF report from CSV data with metadata (v2) - Backward compatibility wrapper.
    
    Args:
        csv_file_path: Path to the CSV file
        output_pdf_path: Optional custom output path for PDF. If None, will be generated
        
    Returns:
        str: Path to the created PDF file
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        Exception: If PDF creation fails
    """
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Read CSV data
    df = pd.read_csv(csv_file_path)
    
    # Extract metadata
    metadata = extract_metadata_from_filename_v2(csv_file_path)
    
    # Generate PDF filename if not provided
    if output_pdf_path is None:
        csv_dir = os.path.dirname(csv_file_path)
        csv_basename = os.path.splitext(os.path.basename(csv_file_path))[0]
        output_pdf_path = os.path.join(csv_dir, f"{csv_basename}.pdf")
    
    # Use the enhanced function
    return create_pdf_from_dataframe_v2(
        df=df,
        query=metadata['query'],
        api_totals={'total': len(df)},
        extraction_summary={
            'source_file': metadata['filename'],
            'extraction_date': metadata['date'],
            'total_columns': len(df.columns),
            'columns': ', '.join(df.columns)
        },
        output_pdf_path=output_pdf_path
    )


def generate_pdf_report(csv_file_path: str) -> str:
    """
    High-level function to generate PDF report from CSV file (v2).
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        console.print(f"[yellow]Creating PDF report from {csv_file_path}...[/yellow]")
        
        pdf_path = create_pdf_from_csv_v2(csv_file_path)
        
        console.print(f"[green]✅ PDF report created: {pdf_path}[/green]")
        return pdf_path
        
    except FileNotFoundError as e:
        console.print(f"[red]❌ CSV file not found: {e}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]❌ Failed to create PDF: {e}[/red]")
        raise


# Enhanced testing functions
def test_enhanced_pdf_generation():
    """
    Test the enhanced PDF generation with comprehensive sample data (v2).
    """
    console.print("\n[bold blue]🧪 Testing Enhanced PDF Generator[/bold blue]")
    
    # Create comprehensive sample data with many columns to trigger landscape mode
    enhanced_sample_data = {
        'id': ['1', '2', '3', '4', '5'],
        'email': ['john.doe@company.com', 'jane.smith@example.org', 'bob.wilson@test.net', 'alice@secure.gov', 'complete@example.com'],
        'password': ['mypassword123', 'securepass456', 'bobspassword', 'alicepass789', 'completeuserdata'],
        'username': ['johndoe', 'janesmith', 'bobwilson', 'alice', 'complete'],
        'domain': ['company.com', 'example.org', 'test.net', 'secure.gov', 'example.com'],
        'phone': ['+1-555-0123', '+1-555-0456', '+1-555-0789', '+1-555-0321', '+1-555-9999'],
        'hash_md5': ['5d41402abc4b2a76b9719d911017c592', '098f6bcd4621d373cade4e832627b4f6', 'aab3238922bcc25a6f606eb525ffdc56', '5d41402abc4b2a76b9719d911017c592', 'e99a18c428cb38d5f260853678922e03'],
        'registration_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12']
    }
    
    df = pd.DataFrame(enhanced_sample_data)
    
    try:
        # Test the enhanced function directly
        output_path = "test_enhanced_report.pdf"
        
        pdf_path = create_pdf_from_dataframe_v2(
            df=df,
            query="example.com",
            api_totals={
                'total': 150,
                'success': True,
                'entries_returned': len(df)
            },
            extraction_summary={
                'original_entries': 150,
                'cleaned_entries': len(df),
                'dropped_entries': 145,
                'unique_emails': df['email'].nunique(),
                'unique_domains': df['domain'].nunique(),
                'hash_columns_detected': ['hash_md5']
            },
            hash_crack_results={
                'hashes_attempted': 5,
                'hashes_cracked': 3,
                'success_rate': '60%',
                'crack_time': '2.5 minutes',
                'wordlist_used': 'rockyou.txt'
            },
            output_pdf_path=output_path
        )
        
        console.print(f"[green]✅ Enhanced PDF test created: {pdf_path}[/green]")
        console.print(f"[cyan]📄 Features tested:[/cyan]")
        console.print(f"   • [yellow]Auto-landscape orientation:[/yellow] {len(df.columns)} columns detected")
        console.print(f"   • [yellow]Cover page with metadata:[/yellow] Query, datetime, API totals")
        console.print(f"   • [yellow]Extraction summary:[/yellow] Embedded in cover page")
        console.print(f"   • [yellow]Hash cracking results:[/yellow] Step 6 integration")
        console.print(f"   • [yellow]Alternating row colors:[/yellow] ReportLab Table styling")
        console.print(f"   • [yellow]All columns rendered:[/yellow] {', '.join(df.columns)}")
        
        return pdf_path
        
    except Exception as e:
        console.print(f"[red]❌ Enhanced PDF test failed: {e}[/red]")
        raise


def test_pdf_generation_v2():
    """
    Test the PDF generation with sample data (v2) - Basic compatibility test.
    """
    import tempfile
    
    console.print("\n[bold blue]🧪 Testing Basic PDF Generator (Backward Compatibility)[/bold blue]")
    
    # Create sample CSV data
    sample_data = {
        'email': ['user1@example.com', 'user2@test.org', 'admin@company.net'],
        'password': ['password123', 'secret456', 'admin789']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test_example.com.csv', delete=False) as f:
        csv_path = f.name
        df.to_csv(csv_path, index=False)
    
    try:
        # Generate PDF
        pdf_path = generate_pdf_report(csv_path)
        console.print(f"[green]✅ Basic PDF test created: {pdf_path}[/green]")
        
        # Clean up
        os.unlink(csv_path)
        
        return pdf_path
        
    except Exception as e:
        console.print(f"[red]❌ Basic PDF test failed: {e}[/red]")
        # Clean up on failure
        if os.path.exists(csv_path):
            os.unlink(csv_path)
        raise


if __name__ == "__main__":
    # Run tests when script is executed directly
    console.print("[bold green]🚀 PDF Generator V2 Test Suite[/bold green]")
    
    try:
        # Test basic functionality first
        basic_pdf = test_pdf_generation_v2()
        
        # Test enhanced functionality
        enhanced_pdf = test_enhanced_pdf_generation()
        
        console.print("\n[bold green]🎉 All PDF generation tests completed successfully![/bold green]")
        console.print(f"[cyan]📁 Generated files:[/cyan]")
        console.print(f"   • Basic PDF: {basic_pdf}")
        console.print(f"   • Enhanced PDF: {enhanced_pdf}")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Test suite failed: {e}[/bold red]")
        raise
