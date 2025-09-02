# Dehashed API Tool

🔍 **A powerful command-line interface for interacting with the DeHashed API** to search for compromised credentials by domain or email address. This tool provides an intuitive interface with rich text formatting, automated result processing, comprehensive reporting capabilities, and **integrated hash cracking functionality**.

## 🚀 v2 Quick-Start Guide

**New to v2? Get started in 3 minutes:**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/dehashed-tool.git
cd dehashed-tool
pip install -r requirements.txt

# 2. Set API credentials (get from dehashed.com)
export DEHASHED_EMAIL="your-email@example.com"
export DEHASHED_API_KEY="your-api-key-here"

# 3. Run v2 with enhanced features
python main_v2.py
```

**✨ What's New in v2:**
- 🔓 **Hash Cracking Integration**: Automatic hashcat/john integration
- 📊 **Enhanced Rich Tables**: Beautiful terminal output with color coding
- 🧠 **Dynamic Field Extraction**: Captures ALL API fields automatically
- 📄 **Improved PDF Reports**: Enhanced layout with cracking statistics
- 🔧 **Tool Coexistence**: v1 and v2 run side-by-side

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
<a href="https://ko-fi.com/macedo84">
<img width="30" height="15" alt="image" src="https://github.com/user-attachments/assets/22212ccb-dd5c-4040-a0af-a63aa3b99376"  />
</a>

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
   # Install core dependencies
   pip install -r requirements.txt
   
   # Or install v2 specific requirements
   pip install -r requirements_v2.txt
   
   # For manual installation of core packages:
   pip install requests pandas rich reportlab python-dotenv
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

## 🔓 Hash Cracking Integration (v2)

**v2 features integrated hash cracking capabilities using popular tools like hashcat and john.**

### Prerequisites for Hash Cracking

**Required Tools:**
- **Hashcat**: Download from [https://hashcat.net/hashcat/](https://hashcat.net/hashcat/)
- **John the Ripper**: Download from [https://www.openwall.com/john/](https://www.openwall.com/john/)

**Installation:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install hashcat john

# Windows (using Chocolatey)
choco install hashcat
# John needs manual installation on Windows

# macOS (using Homebrew)
brew install hashcat john
```

**Wordlists:**
```bash
# Download popular wordlists
wget https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz
tar -xzf rockyou.txt.tar.gz

# Or use system wordlists
# Linux: /usr/share/wordlists/
# Kali: /usr/share/wordlists/rockyou.txt
```

### Hash Cracking Workflow

**1. Run v2 with Hash Detection:**
```bash
python main_v2.py
```

**2. Automatic Hash Detection:**
- v2 automatically detects hash columns in API responses
- Supports: MD5, SHA1, SHA256, SHA512, NTLM, bcrypt, and more
- Uses pattern matching and data analysis for detection

**3. Interactive Cracking Process:**
```
📊 Hash columns detected: ['password_hash', 'ntlm_hash']
🔓 Do you want to attempt to crack the hashes? (y/n): y

🔧 Available Cracking Tools:
1) hashcat (installed)
2) john (installed)

Select a tool [1/2] (1): 1
Enter hash type or leave empty for auto-detect: 
Enter path to wordlist [rockyou.txt]: /usr/share/wordlists/rockyou.txt

🚀 Proceed with hashcat using hash file temp_hashes.txt with wordlist rockyou.txt? (y/n): y
```

**4. Real-time Cracking Progress:**
```
┌─ Cracking ──────────────────────────────────┐
│ hashcat (v6.2.6) starting...              │
│ Session..........: hashcat                 │
│ Status...........: Running                 │
│ Progress.........: 1024/14344385 (0.01%)   │
│ Speed.#.1........: 2847.3 kH/s (0.92ms)   │
└─────────────────────────────────────────────┘
```

**5. Results Integration:**
```
✅ Cracking completed successfully.
📊 Final statistics for query 'example.com':
   Total entries processed: 25
   Cracked passwords: 12
✅ Cracked results saved to output/2025-07-24_example.com_cracked.csv
✅ Updated PDF report saved to output/2025-07-24_example.com.pdf
```

### Hash Cracking Features

**🎯 Intelligent Hash Detection:**
- Automatic identification of hash columns
- Support for nested JSON fields
- Pattern-based and content-based detection
- Common hash formats: MD5, SHA*, NTLM, bcrypt, scrypt

**🔧 Tool Integration:**
- **Hashcat**: GPU-accelerated cracking with mode auto-detection
- **John the Ripper**: CPU-based cracking with format detection
- Automatic tool detection and selection
- Custom wordlist support

**📈 Progress Monitoring:**
- Real-time progress display using Rich panels
- Live updates on cracking status
- Duration tracking and statistics
- Success/failure reporting

**💾 Result Management:**
- Automatic integration of cracked passwords into dataset
- Separate `_cracked.csv` files for results with cracked passwords
- Updated PDF reports with cracking statistics
- Preservation of original data alongside cracked results

### Advanced Hash Cracking

**Custom Hash Types:**
```python
# For advanced users: manual hash type specification
# Hashcat mode examples:
# 0 = MD5
# 100 = SHA1  
# 1000 = NTLM
# 3200 = bcrypt
```

**Performance Optimization:**
```bash
# GPU acceleration (if available)
export CUDA_VISIBLE_DEVICES=0

# Custom hashcat options
export HASHCAT_OPTS="--force --optimized-kernel-enable"
```

**Batch Processing:**
```python
# Process multiple hash types simultaneously
# v2 automatically handles multiple hash columns
# Results are merged and presented in unified format
```

### Hash Cracking Best Practices

**🔒 Security:**
- Only crack hashes you have authorization to crack
- Use dedicated, isolated systems for cracking
- Secure disposal of temporary hash files
- Follow responsible disclosure practices

**⚡ Performance:**
- Use GPU acceleration when available (hashcat)
- Start with smaller, targeted wordlists
- Consider distributed cracking for large datasets
- Monitor system resources during intensive operations

**📝 Documentation:**
- Document cracking attempts and results
- Maintain audit trails for security assessments
- Record successful cracking methods for future reference
- Include cracking statistics in security reports

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

## 📋 Requirements & Dependencies

### Core Dependencies (v1 & v2)

**Essential packages for all functionality:**
```bash
# Core API and data processing
pip install requests>=2.25.0      # HTTP API communication
pip install pandas>=2.0.0         # Data processing and CSV export
pip install numpy>=1.21.0         # Numerical operations

# User interface and formatting
pip install rich>=13.0.0          # Terminal formatting and UI
pip install python-dotenv>=0.19.0 # Environment variable management

# PDF generation
pip install reportlab>=4.0.0      # PDF report generation
pip install pillow>=9.0.0         # Image processing for PDFs
```

### v2 Enhanced Dependencies

**Additional packages for v2 hash cracking features:**
```bash
# Enhanced CLI framework (v2)
pip install typer>=0.9.0          # Advanced CLI framework
pip install click>=8.0.0          # CLI utilities

# Console enhancements
pip install colorama>=0.4.6       # Cross-platform color support
pip install shellingham>=1.5.0    # Shell detection
```

### External Tools (Hash Cracking)

**Required for v2 hash cracking functionality:**

| Tool | Purpose | Installation Command |
|------|---------|---------------------|
| **Hashcat** | GPU-accelerated hash cracking | `sudo apt install hashcat` (Linux)<br>`brew install hashcat` (macOS)<br>`choco install hashcat` (Windows) |
| **John the Ripper** | CPU-based hash cracking | `sudo apt install john` (Linux)<br>`brew install john` (macOS)<br>Manual install (Windows) |

### Complete Installation Guide

**Method 1: Automated Installation (Recommended)**
```bash
# For v1 compatibility
pip install -r requirements.txt

# For v2 with all features
pip install -r requirements_v2.txt

# Verify installation
python -c "import requests, pandas, rich, reportlab; print('✅ All dependencies installed')"
```

**Method 2: Manual Step-by-Step**
```bash
# Step 1: Core functionality
pip install requests pandas rich

# Step 2: PDF generation
pip install reportlab pillow

# Step 3: Configuration management
pip install python-dotenv

# Step 4: v2 enhancements (optional)
pip install typer click colorama

# Step 5: Verify installation
python main.py --help
```

**Method 3: Development Environment**
```bash
# Clone repository
git clone https://github.com/yourusername/dehashed-tool.git
cd dehashed-tool

# Create isolated environment
python -m venv dehashed_env
source dehashed_env/bin/activate  # Linux/macOS
# OR
dehashed_env\Scripts\activate     # Windows

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test installation
python demo_rich_output.py
```

### Dependency Details

| Package | Version | Purpose | Required For |
|---------|---------|---------|-------------|
| **requests** | ≥2.25.0 | HTTP API communication | v1, v2 |
| **pandas** | ≥2.0.0 | Data processing and CSV export | v1, v2 |
| **rich** | ≥13.0.0 | Terminal formatting and tables | v1, v2 |
| **reportlab** | ≥4.0.0 | PDF report generation | v1, v2 |
| **python-dotenv** | ≥0.19.0 | Environment variable management | v1, v2 |
| **typer** | ≥0.9.0 | Enhanced CLI framework | v2 only |
| **pillow** | ≥9.0.0 | Image processing for PDFs | v1, v2 |
| **numpy** | ≥1.21.0 | Numerical operations | v1, v2 |
| **colorama** | ≥0.4.6 | Cross-platform color support | v2 only |

### Troubleshooting Dependencies

**Common Installation Issues:**

```bash
# Issue: pip install fails with permission errors
# Solution: Use user installation
pip install --user -r requirements.txt

# Issue: reportlab installation fails
# Solution: Install build tools first
# Ubuntu/Debian:
sudo apt install python3-dev build-essential
# CentOS/RHEL:
sudo yum install python3-devel gcc
# Windows: Install Visual Studio Build Tools

# Issue: Rich not displaying colors
# Solution: Install colorama
pip install colorama

# Issue: PDF generation fails
# Solution: Update pillow and reportlab
pip install --upgrade pillow reportlab
```

**Version Compatibility:**

| Python Version | Supported | Notes |
|----------------|-----------|-------|
| 3.7 | ✅ | Minimum required version |
| 3.8 | ✅ | Recommended for stability |
| 3.9 | ✅ | Full feature support |
| 3.10 | ✅ | Full feature support |
| 3.11 | ✅ | Latest features and performance |
| 3.12 | ✅ | Full support with latest packages |

**Platform-Specific Notes:**

- **Windows**: Some packages require Visual Studio Build Tools
- **macOS**: Use Homebrew for external tools (hashcat, john)
- **Linux**: Most packages available through system package manager
- **Docker**: See `Dockerfile` for containerized deployment

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
