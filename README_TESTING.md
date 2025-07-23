# Testing and Dry-Run Documentation

This document describes the comprehensive test suite and dry-run functionality for the Dehashed API tool.

## Overview

The test suite includes:
1. **API Key Retrieval Tests** - Testing key retrieval from environment variables and config files
2. **Rate-Limit Handler Tests** - Testing rate limiting with mocked HTTP responses
3. **CSV/PDF Export Tests** - Testing file creation and existence verification  
4. **Dry-Run Mode Tests** - Testing functionality with mocked API responses
5. **Integration Tests** - End-to-end workflow testing

## Files

### Test Files
- `test_suite.py` - Comprehensive unit test suite
- `simple_demo.py` - Automated demo script
- `dry_run_demo.py` - Interactive dry-run demonstration

## Running Tests

### Full Test Suite
```bash
python test_suite.py --all
```

This runs all 17 tests covering:
- ✅ API key from environment variable
- ✅ API key from config file  
- ✅ API key not found scenarios
- ✅ API key priority (env over config)
- ✅ Rate limit with Retry-After header
- ✅ Rate limit with exponential backoff
- ✅ Rate limit max retries exceeded
- ✅ API error handling
- ✅ CSV file creation and existence
- ✅ PDF generation from CSV
- ✅ Metadata extraction from filename
- ✅ CSV not found error handling
- ✅ Dry-run successful search
- ✅ Dry-run with result extraction
- ✅ Dry-run without real requests
- ✅ End-to-end workflow integration

### Individual Test Classes
```bash
# Run specific test class
python -m unittest test_suite.TestAPIKeyRetrieval
python -m unittest test_suite.TestRateLimitHandler
python -m unittest test_suite.TestCSVPDFExportFunctions
python -m unittest test_suite.TestDryRunMode
python -m unittest test_suite.TestIntegrationScenarios
```

### Quick Demo
```bash
python simple_demo.py
```

This runs an automated demonstration of all functionality with mocked data.

## Dry-Run Mode

### Interactive Demo
```bash
python dry_run_demo.py
```

This provides an interactive demonstration with multiple scenarios:
- `example.com` - Returns 5 sample records
- `testcompany.org` - Returns 3 sample records  
- `user@demo.com` - Returns 1 sample record
- `ratelimit.com` - Simulates rate limiting
- `error.com` - Simulates API errors
- Custom queries - Return empty results

### Automated Demo
```bash
python simple_demo.py
```

This runs through all functionality automatically:
1. **API Key Handling** - Tests environment variable and fallback scenarios
2. **Search Functionality** - Mock API search with data processing
3. **Rate Limiting** - Demonstrates retry logic
4. **File Export** - Creates CSV and PDF files with verification

## Test Categories

### 1. API Key Retrieval Tests

Tests the `get_api_key()` function:
- Environment variable retrieval
- Config file fallback
- Priority handling (env over config)
- Error handling when no key found

```python
def test_api_key_from_environment_variable(self):
    test_key = 'test_env_api_key_123'
    with patch.dict(os.environ, {'DEHASHED_API_KEY': test_key}):
        result = get_api_key()
        self.assertEqual(result, test_key)
```

### 2. Rate-Limit Handler Tests

Tests the rate limiting functionality in `dehashed.search()`:
- Retry-After header handling
- Exponential backoff
- Max retries exceeded
- Various HTTP error codes

```python
@patch('dehashed.requests.post')
@patch('dehashed.time.sleep')
def test_rate_limit_with_retry_after_header(self, mock_sleep, mock_post):
    # First call returns 429, second returns 200
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.headers = {'Retry-After': '2'}
    
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {'success': True, 'entries': []}
    
    mock_post.side_effect = [mock_response_429, mock_response_200]
    result = search(query='test@example.com', api_key='test_key', max_retries=1)
```

### 3. CSV/PDF Export Tests

Tests file creation and verification:
- CSV file creation and content verification
- PDF generation from CSV
- Metadata extraction from filenames  
- Error handling for missing files
- File size validation

```python
def test_csv_file_creation_and_existence(self):
    sample_data = {
        'email': ['user1@example.com', 'user2@test.org'],
        'password': ['password123', 'secret456']
    }
    df = pd.DataFrame(sample_data)
    df.to_csv(self.csv_file, index=False)
    
    # Verify file exists and has correct content
    self.assertTrue(os.path.exists(self.csv_file))
    loaded_df = pd.read_csv(self.csv_file)
    self.assertEqual(len(loaded_df), 2)
```

### 4. Dry-Run Mode Tests

Tests functionality with mocked API responses:
- Successful API responses
- Data extraction and filtering
- Complete workflow without real API calls
- Error scenario simulation

```python
@patch('dehashed.requests.post')
def test_dry_run_successful_search(self, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'total': 2,
        'entries': [
            {
                'id': '1',
                'email': 'user1@example.com',
                'password': 'password123'
            }
        ]
    }
    mock_post.return_value = mock_response
    
    result = search(query='example.com', api_key='dry_run_key')
    self.assertTrue(result['success'])
```

### 5. Integration Tests

Tests complete end-to-end workflows:
- API search → data extraction → CSV export → PDF generation
- Verifies data flows correctly between components
- Tests file creation and cleanup

## Sample Output

### Test Suite Results
```
🧪 Running Dehashed API Tool Test Suite

test_api_key_from_environment_variable ... ✅ API key from environment variable test passed
test_rate_limit_with_retry_after_header ... ✅ Rate limit with Retry-After header test passed
test_csv_file_creation_and_existence ... ✅ CSV file creation and existence test passed
test_dry_run_successful_search ... ✅ Dry-run successful search test passed

Test Summary:
  • Tests run: 17
  • Failures: 0
  • Errors: 0

✅ All tests passed successfully!
```

### Demo Output
```
🧪 Dehashed API Tool - Automated Demo

🔑 API Key Functionality Demo
✅ Environment variable: demo_env_key_12...
⚠️  No key found: None

🔍 Search Functionality Demo
✅ Mock API search completed
Original entries: 3
Valid email/password pairs: 2

💾 File Export Demo
✅ CSV created: 2024-01-15_demo_export.csv
✅ PDF created: 2024-01-15_demo_export.pdf
✅ CSV exists: True
✅ PDF exists: True

🎉 All demos completed successfully!
```

## Benefits

### No Real API Key Required
- All tests use mocked responses
- Safe to run in CI/CD environments
- No risk of hitting rate limits during testing

### Comprehensive Coverage
- Tests all major functionality
- Covers error scenarios
- Validates file operations

### Easy to Run
- Single command execution
- Clear pass/fail indicators
- Detailed output and logging

### Development Support
- Helps verify changes don't break functionality
- Provides examples of expected behavior
- Enables confident refactoring

## Usage in Development

### Before Committing Changes
```bash
python test_suite.py --all
```

### Demonstrating Functionality
```bash
python simple_demo.py
```

### Interactive Testing
```bash
python dry_run_demo.py
```

This comprehensive test suite ensures the reliability and functionality of the Dehashed API tool while providing multiple ways to demonstrate and verify its capabilities without requiring real API credentials.
