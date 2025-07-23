#!/usr/bin/env python3
"""
PDF generator module for Dehashed API results.

This module provides functionality to create PDF reports from CSV data
using ReportLab, including metadata and formatted tables.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from rich.console import Console

console = Console()


def extract_metadata_from_filename(csv_filename: str) -> dict:
    """
    Extract metadata from CSV filename.
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


def create_pdf_from_csv(csv_file_path: str, output_pdf_path: Optional[str] = None) -> str:
    """
    Create a PDF report from CSV data with metadata.
    
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
    metadata = extract_metadata_from_filename(csv_file_path)
    record_count = len(df)
    
    # Generate PDF filename if not provided
    if output_pdf_path is None:
        csv_dir = os.path.dirname(csv_file_path)
        csv_basename = os.path.splitext(os.path.basename(csv_file_path))[0]
        output_pdf_path = os.path.join(csv_dir, f"{csv_basename}.pdf")
    
    # Create PDF
    try:
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        # Add title
        title = Paragraph("Dehashed API Search Results", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add metadata section
        metadata_heading = Paragraph("Search Metadata", heading_style)
        elements.append(metadata_heading)
        
        metadata_table_data = [
            ['Date:', metadata['date']],
            ['Query:', metadata['query']],
            ['Total Records:', str(record_count)],
            ['Source File:', metadata['filename']]
        ]
        
        metadata_table = Table(metadata_table_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 20))
        
        # Add data table section
        if record_count > 0:
            data_heading = Paragraph("Email and Password Data", heading_style)
            elements.append(data_heading)
            
            # Prepare table data
            table_data = [['Email', 'Password']]  # Header row
            
            # Add data rows (limit to prevent overly large PDFs)
            max_rows = 100  # Limit for readability
            rows_to_show = min(record_count, max_rows)
            
            for i in range(rows_to_show):
                row = df.iloc[i]
                email = str(row['email']) if pd.notna(row['email']) else ''
                password = str(row['password']) if pd.notna(row['password']) else ''
                table_data.append([email, password])
            
            # Add truncation notice if needed
            if record_count > max_rows:
                table_data.append([f'... ({record_count - max_rows} more records)', '(truncated for display)'])
            
            # Create table
            data_table = Table(table_data, colWidths=[3*inch, 3*inch])
            data_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Alternating row colors
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, 2), (-1, -1), colors.white),
            ]))
            
            # Apply alternating row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    data_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                    ]))
            
            elements.append(data_table)
        else:
            no_data_msg = Paragraph("No data records found.", styles['Normal'])
            elements.append(no_data_msg)
        
        # Add footer with generation timestamp
        elements.append(Spacer(1, 30))
        footer_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        return output_pdf_path
        
    except Exception as e:
        raise Exception(f"Failed to create PDF: {str(e)}")


def generate_pdf_report(csv_file_path: str) -> str:
    """
    High-level function to generate PDF report from CSV file.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        console.print(f"[yellow]Creating PDF report from {csv_file_path}...[/yellow]")
        
        pdf_path = create_pdf_from_csv(csv_file_path)
        
        console.print(f"[green]✅ PDF report created: {pdf_path}[/green]")
        return pdf_path
        
    except FileNotFoundError as e:
        console.print(f"[red]❌ CSV file not found: {e}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]❌ Failed to create PDF: {e}[/red]")
        raise


# Example usage and testing function
def test_pdf_generation():
    """
    Test the PDF generation with sample data.
    """
    import tempfile
    
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
        console.print(f"[green]✅ Test PDF created at: {pdf_path}[/green]")
        
        # Clean up
        os.unlink(csv_path)
        
        return pdf_path
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        # Clean up on failure
        if os.path.exists(csv_path):
            os.unlink(csv_path)
        raise


if __name__ == "__main__":
    # Run test when script is executed directly
    test_pdf_generation()
