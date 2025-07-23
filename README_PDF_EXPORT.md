# PDF Export Documentation

This documentation covers the PDF export functionality for the Dehashed API tool.

## Overview

The tool now automatically generates PDF reports alongside CSV files when performing searches. The PDF reports contain:

- **Search metadata**: Date, query string, and record count
- **Data table**: Email and password pairs in a formatted table
- **Professional formatting**: Clean layout with headers, styling, and timestamps

## Files Involved

### Core Modules

- **`pdf_generator.py`**: Main PDF generation module using ReportLab
- **`main.py`**: Modified to automatically generate PDFs after CSV export
- **`create_pdf_from_csv.py`**: Utility script for batch/manual PDF generation

### Dependencies

- **ReportLab**: PDF generation library
- **pandas**: Data manipulation
- **rich**: Console formatting

## Automatic PDF Generation

When you run the main application and perform a search, both CSV and PDF files are automatically created:

```bash
python main.py
```

Example output:
```
✅ Dataframe saved to output/2025-01-23_example.com.csv
✅ PDF report saved to output/2025-01-23_example.com.pdf
```

## Manual PDF Generation

### Generate PDF from Specific CSV

```bash
python create_pdf_from_csv.py output/2025-01-23_example.com.csv
```

### Batch Process All CSV Files

```bash
python create_pdf_from_csv.py --batch
```

### Custom Output Directory

```bash
python create_pdf_from_csv.py --batch --output-dir reports/
```

## PDF Content Structure

### 1. Title Section
- "Dehashed API Search Results" centered header

### 2. Metadata Table
- **Date**: Search execution date
- **Query**: Original search term/domain
- **Total Records**: Number of email/password pairs found
- **Source File**: Name of the CSV file

### 3. Data Table
- **Email column**: Email addresses with domain highlighting
- **Password column**: Passwords with color coding by length
- **Row limit**: Maximum 100 rows (with truncation notice if needed)
- **Alternating row colors**: For better readability

### 4. Footer
- Generation timestamp

## PDF Features

### Professional Formatting
- A4 page size with proper margins
- Color-coded headers and sections
- Grid-based table layout
- Professional fonts (Helvetica family)

### Data Protection
- Large datasets are truncated to 100 rows for PDF readability
- Truncation is clearly indicated in the PDF
- Full data remains available in CSV format

### Error Handling
- Graceful handling of missing or corrupted CSV files
- Non-blocking errors (CSV still saves if PDF generation fails)
- Detailed error messages with Rich formatting

## File Naming Convention

PDF files follow the same naming pattern as CSV files:
- Format: `YYYY-MM-DD_query.pdf`
- Example: `2025-01-23_example.com.pdf`
- Location: Same directory as the CSV file

## Usage Examples

### Scenario 1: Normal Search Operation
```bash
# Run normal search - both CSV and PDF are created automatically
python main.py
# Select domain search, enter "example.com"
# Output: 
#   output/2025-01-23_example.com.csv
#   output/2025-01-23_example.com.pdf
```

### Scenario 2: Retroactive PDF Generation
```bash
# Generate PDFs for existing CSV files
python create_pdf_from_csv.py --batch
```

### Scenario 3: Single File Conversion
```bash
# Convert specific CSV to PDF
python create_pdf_from_csv.py output/old_file.csv
```

## Technical Details

### PDF Library: ReportLab
- Industry-standard Python PDF generation library
- Supports tables, styling, and professional layouts
- Cross-platform compatibility

### Metadata Extraction
The tool automatically extracts metadata from CSV filenames:
- Parses date from filename (YYYY-MM-DD format)
- Extracts query string from filename
- Counts records from CSV data
- Handles various filename formats gracefully

### Memory Efficiency
- Streams data processing for large CSV files
- Limits PDF table rows to prevent excessive memory usage
- Maintains full data integrity in CSV while providing readable PDF summaries

## Troubleshooting

### Common Issues

**PDF Generation Fails**
- Check ReportLab installation: `pip install reportlab`
- Verify CSV file exists and is readable
- Ensure write permissions in output directory

**Memory Issues with Large Files**
- PDFs automatically limit to 100 rows for performance
- Consider splitting very large datasets before processing

**File Permission Errors**
- Ensure output directory is writable
- Close PDF files if they're open in viewers before regenerating

### Error Messages

- `❌ CSV file not found`: Check file path and existence
- `⚠️ PDF generation failed`: Check ReportLab installation and permissions
- `❌ No CSV files to process`: Verify batch processing directory contains CSV files

## Configuration

### Customizing PDF Appearance

Edit `pdf_generator.py` to modify:
- Page size (default: A4)
- Margins and spacing
- Colors and fonts
- Table row limits
- Header and footer content

### Example Customizations

```python
# Change page size to Letter
pagesize=letter

# Modify table row limit
max_rows = 50  # Show fewer rows

# Change color scheme
colors.darkblue  # Header color
colors.lightgrey  # Alternating row color
```

## Best Practices

1. **Keep CSV and PDF together**: Store both files in the same directory
2. **Use batch processing**: For multiple files, use `--batch` mode
3. **Regular cleanup**: Archive old reports to prevent directory clutter
4. **Backup important data**: PDF is for reporting, CSV contains full data
5. **Check file sizes**: Large PDFs may indicate need for data filtering

## Integration Notes

The PDF functionality is seamlessly integrated into the existing workflow:
- No changes required to existing search procedures
- CSV functionality remains unchanged
- PDF generation is non-blocking (won't prevent CSV creation)
- Rich console formatting provides clear status updates

## Support

For issues related to PDF generation:
1. Check ReportLab installation and version
2. Verify CSV file format and content
3. Review error messages in console output
4. Test with sample data using `test_pdf_integration.py`
