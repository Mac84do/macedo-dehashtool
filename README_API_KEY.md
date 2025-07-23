# API Key Storage

This project implements secure API key storage for the DeHashed API with two options:

## Option 1: Environment Variable (Preferred)

Set the `DEHASHED_API_KEY` environment variable:

### Windows
```cmd
set DEHASHED_API_KEY=your_api_key_here
```

### Linux/macOS
```bash
export DEHASHED_API_KEY=your_api_key_here
```

### Permanent Setup
For permanent setup, add the environment variable to your system or shell configuration:

- **Windows**: Use System Properties → Environment Variables
- **Linux/macOS**: Add `export DEHASHED_API_KEY=your_api_key_here` to your `~/.bashrc`, `~/.zshrc`, or equivalent

## Option 2: Configuration File

1. Copy the example configuration file:
   ```bash
   cp config.ini.example config.ini
   ```

2. Edit `config.ini` and replace `your_api_key_here` with your actual API key:
   ```ini
   [DEFAULT]
   DEHASHED_API_KEY = your_actual_api_key_here
   ```

3. The `config.ini` file is automatically git-ignored for security.

## Usage

Use the `get_api_key()` function to retrieve the API key:

```python
from get_api_key import get_api_key

api_key = get_api_key()
if api_key:
    print("API key loaded successfully")
else:
    print("No API key found - please configure one")
```

## Security Features

- **Environment variable priority**: Environment variables are checked first as they are more secure
- **Git-ignored config**: The `config.ini` file is automatically excluded from version control
- **No hardcoded keys**: API keys are never stored in source code
- **Graceful fallback**: The function returns `None` if no key is found, allowing for proper error handling

## Testing

Run the example script to test your API key configuration:

```bash
python example_usage.py
```

This will show whether your API key is properly configured and provide setup instructions if needed.
