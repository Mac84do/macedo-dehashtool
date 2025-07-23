#!/usr/bin/env python3
"""
Example usage of the get_api_key() function.

This script demonstrates how to use the API key retrieval function
that checks environment variables first, then falls back to config.ini.
"""

from get_api_key import get_api_key

def main():
    # Get the API key using the secure storage method
    api_key = get_api_key()
    
    if api_key:
        print("✓ API key found and loaded successfully")
        print(f"Key starts with: {api_key[:8]}..." if len(api_key) > 8 else "Key is too short")
    else:
        print("✗ No API key found!")
        print("\nTo set up your API key, choose one of these options:")
        print("\nOption 1 (Preferred): Set environment variable")
        print("  Windows: set DEHASHED_API_KEY=your_api_key_here")
        print("  Linux/Mac: export DEHASHED_API_KEY=your_api_key_here")
        print("\nOption 2: Create config.ini file")
        print("  1. Copy config.ini.example to config.ini")
        print("  2. Edit config.ini and replace 'your_api_key_here' with your actual API key")
        print("  3. The config.ini file is already git-ignored for security")

if __name__ == "__main__":
    main()
