# Dehashed API Tool

A powerful command-line interface for interacting with the DeHashed API to search for compromised credentials by domain or email address. This tool provides an intuitive interface with rich text formatting, automated result processing, and comprehensive reporting capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)

## ✨ Features

### 🔍 **Comprehensive Search Capabilities**
- **Domain Search**: Search for all compromised credentials associated with a specific domain
- **Email Search**: Search for compromised credentials for specific email addresses
- **Interactive CLI**: User-friendly command-line interface with rich text formatting and prompts

### 📊 **Advanced Result Processing**
- **Data Extraction**: Automatically extracts email and password pairs from API responses
- **Data Cleaning**: Removes null, empty, and invalid entries from results
- **Statistical Summary**: Provides detailed statistics about found credentials and duplicates

### 📁 **Export & Reporting**
- **CSV Export**: Automatically saves results to timestamped CSV files
- **PDF Reports**: Generates professional PDF reports with metadata and formatted tables
- **Rich Console Output**: Beautiful terminal output with syntax highlighting and tables

### 🛡️ **Security & Reliability**
- **Secure API Key Storage**: Multiple options for secure API key management
- **Rate Limit Handling**: Automatic retry logic with exponential backoff
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Input Validation**: Validates user input and API responses

## 📷 Screenshots

### Main Interface
```
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────── Dehashed API Tool ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                        │
│  Welcome to the Dehashed API search tool!                                                                                                                                                                                              │
│  Search for compromised credentials by domain or email address.                                                                                                                                                                        │
│  Built with ❤️  for security research.                                                                                                                                                                                                 │
│                                                                                                                                                                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✅ API key loaded successfully

Search Options:
1) Domain search
2) Email search

Select search type [1/2] (1):
```

### Search Results Example
```
📊 Extraction Summary:
   • Final records: 15
   • Original entries: 18
   • Dropped (null/empty): 3
   • Unique emails: 12
   • Unique passwords: 14

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Email                                        ┃ Password                                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ user@example.com                             │ password123                                    │
│ admin@example.com                            │ secretpassword                                 │
└──────────────────────────────────────────────┴────────────────────────────────────────────────┘

✅ Dataframe saved to output/2025-01-23_example.com.csv
✅ PDF report saved to output/2025-01-23_example.com.pdf
```

## 🔑 Obtaining DeHashed API Key

To use this tool, you need a DeHashed API key:

1. **Visit DeHashed**: Go to [https://www.dehashed.com](https://www.dehashed.com)
2. **Create Account**: Register for a new account
3. **Choose Plan**: Subscribe to a plan that fits your needs:
   - **Personal**: For individual researchers
   - **Professional**: For security professionals
   - **Enterprise**: For organizations
4. **Get API Key**: Navigate to your account settings to obtain your API key
5. **Note Limits**: Each plan has different rate limits and query quotas

### API Key Verification
You can verify your API key works by visiting the DeHashed API documentation or using their test endpoints.

## 🚀 Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Valid DeHashed API key

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/dehashed-tool.git
   cd dehashed-tool
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key** (See Environment Variables section below)

5. **Test Installation**
   ```bash
   python main.py
   ```

## 🔧 Environment Variables

### Option 1: Environment Variable (Recommended)

Set the `DEHASHED_API_KEY` environment variable:

**Windows:**
```cmd
# Temporary (current session)
set DEHASHED_API_KEY=your_api_key_here

# Permanent (add to system environment variables)
setx DEHASHED_API_KEY "your_api_key_here"
```

**Linux/macOS:**
```bash
# Temporary (current session)
export DEHASHED_API_KEY=your_api_key_here

# Permanent (add to shell profile)
echo 'export DEHASHED_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

**Python .env file:**
```bash
# Create .env file in project root
echo "DEHASHED_API_KEY=your_api_key_here" > .env
```

### Option 2: Configuration File

1. **Copy Example Configuration:**
   ```bash
   cp config.ini.example config.ini
   ```

2. **Edit Configuration:**
   ```ini
   [DEFAULT]
   DEHASHED_API_KEY = your_actual_api_key_here
   ```

3. **File is Git-ignored** for security

## 💻 Usage Examples

### Basic Usage

```bash
# Run the interactive CLI
python main.py
```

### Programmatic Usage

```python
from dehashed import search
from result_extraction import extract_email_password_data
from get_api_key import get_api_key

# Get API key
api_key = get_api_key()

# Perform search
response = search(query="example.com", api_key=api_key)

# Extract and process results
df = extract_email_password_data(response)
print(f"Found {len(df)} valid email/password pairs")
```

### Advanced Usage Examples

```python
# Search by email
response = search(query="user@example.com", api_key=api_key)

# Search with custom retry logic
response = search(query="example.com", api_key=api_key, max_retries=5)

# Generate PDF report from existing CSV
from pdf_generator import generate_pdf_report
pdf_path = generate_pdf_report("output/2025-01-23_example.com.csv")
```

### Demo Scripts

The project includes several demo scripts:

```bash
# Test result extraction
python demo_result_extraction.py

# Test rich output formatting
python demo_rich_output.py

# Test dry run functionality
python dry_run_demo.py

# Simple usage demonstration
python simple_demo.py
```

## 📁 Output Files

The tool automatically creates organized output files:

```
output/
├── 2025-01-23_example.com.csv      # CSV data export
├── 2025-01-23_example.com.pdf      # PDF report
├── 2025-01-23_user@domain.com.csv  # Email search results
└── 2025-01-23_user@domain.com.pdf  # Email search PDF
```

### File Naming Convention
- Format: `YYYY-MM-DD_query.csv/pdf`
- Special characters in queries are replaced with underscores
- Files are organized by date for easy management

## 🛡️ Security Considerations

### API Key Security
- **Never hardcode** API keys in source code
- **Use environment variables** or secure configuration files
- **Rotate keys regularly** as per security best practices
- **Monitor usage** through DeHashed dashboard to detect unauthorized access

### Data Handling
- **Sensitive data**: Results contain potentially sensitive credential information
- **Local storage**: CSV/PDF files are stored locally - secure your file system
- **Access control**: Implement appropriate file permissions on output directories
- **Data retention**: Establish policies for how long to retain exported data

### Network Security
- **HTTPS**: All API communications use HTTPS
- **Rate limiting**: Built-in rate limiting prevents abuse
- **Error handling**: Secure error messages that don't leak sensitive information

### Best Practices
1. **Secure your environment**: Use secure systems for running the tool
2. **Regular updates**: Keep dependencies updated for security patches
3. **Audit trails**: Monitor and log tool usage appropriately
4. **Access management**: Limit tool access to authorized personnel only
5. **Data encryption**: Consider encrypting output files for additional security

## 📊 Error Handling

The tool includes comprehensive error handling:

### API Errors
- **401 Unauthorized**: Invalid or missing API key
- **429 Rate Limited**: Automatic retry with exponential backoff
- **403 Forbidden**: Insufficient permissions or quota exceeded
- **500 Server Error**: DeHashed API issues

### Input Validation
- **Empty queries**: Validates user input before API calls
- **Invalid formats**: Checks email format and domain validity
- **Network issues**: Handles connection timeouts and failures

### Example Error Messages
```
❌ No API key found!

Please set up your API key first:
1. Set environment variable: DEHASHED_API_KEY=your_key
2. Or create config.ini from config.ini.example

See README_API_KEY.md for detailed instructions.
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test_suite.py

# Test PDF integration
python test_pdf_integration.py

# Test specific modules
python -m pytest tests/ -v
```

## 📚 Code Documentation

All modules include comprehensive docstrings following Python standards:

### Example Function Documentation
```python
def search(query: str, api_key: str, max_retries: int = 3) -> Dict[Any, Any]:
    """
    Search the DeHashed API with the given query.
    
    Args:
        query: The search query string (domain or email)
        api_key: The API key for authentication
        max_retries: Maximum number of retry attempts for rate limiting
        
    Returns:
        Dictionary containing the API response with entries
        
    Raises:
        DeHashedRateLimitError: When rate limit is exceeded and retries are exhausted
        DeHashedAPIError: For other API errors (non-200 status codes)
        DeHashedError: For other general errors
        
    Example:
        >>> response = search("example.com", "your_api_key")
        >>> print(f"Found {len(response['entries'])} entries")
    """
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 .

# Run type checking
mypy .

# Format code
black .
```

## 📋 Requirements

See `requirements.txt` for detailed dependency list:

- **requests**: HTTP API communication
- **pandas**: Data processing and CSV export
- **rich**: Terminal formatting and UI
- **reportlab**: PDF generation
- **python-dotenv**: Environment variable management
- **typer**: CLI framework (for future enhancements)
- **pillow**: Image processing for PDF reports

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Check the existing markdown files for specific topics:
  - `README_API_KEY.md`: API key configuration details
  - `README_PDF_EXPORT.md`: PDF generation documentation
  - `README_TESTING.md`: Testing guidelines
- **Security**: For security concerns, please email [security@example.com]

## 🏆 Acknowledgments

- **DeHashed**: For providing the API service for security research
- **Rich**: For the beautiful terminal interface library
- **ReportLab**: For PDF generation capabilities
- **Community**: For feedback and contributions

---

**⚠️ Disclaimer**: This tool is intended for legitimate security research and authorized testing only. Users are responsible for ensuring compliance with applicable laws and regulations.
