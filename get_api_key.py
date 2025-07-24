#!/usr/bin/env python3
"""
Secure API key retrieval module for DeHashed API Tool.

This module provides secure API key storage and retrieval functionality
with multiple fallback options prioritizing environment variables for
enhanced security. The module supports both environment variable and
configuration file storage methods.

Security Features:
- Environment variable priority (most secure)
- Configuration file fallback
- No hardcoded keys in source code
- Graceful error handling for missing keys

Example:
    >>> from get_api_key import get_api_key
    >>> api_key = get_api_key()
    >>> if api_key:
    >>>     print("API key loaded successfully")
    >>> else:
    >>>     print("No API key found")
"""

import os
from configparser import ConfigParser, NoSectionError, NoOptionError


def get_api_key():
    """
    Retrieve DeHashed API key from secure storage locations.
    
    Attempts to retrieve the API key using multiple secure methods with
    priority given to environment variables for enhanced security.
    
    Search Order:
    1. DEHASHED_API_KEY environment variable (preferred)
    2. config.ini file [DEFAULT] section (fallback)
    
    The function prioritizes environment variables because they are:
    - More secure (not stored in files)
    - Easier to manage in different environments
    - Standard practice for sensitive configuration
    
    Returns:
        str or None: The API key if found, None if no key is available
        
    Raises:
        No exceptions are raised; errors are handled gracefully
        
    Security Notes:
        - Environment variables are checked first for security
        - Configuration files are git-ignored
        - No API keys are logged or printed
        - Function fails gracefully if no key is found
        
    Example:
        >>> api_key = get_api_key()
        >>> if api_key:
        >>>     print("API key loaded successfully")
        >>>     # Use api_key for API calls
        >>> else:
        >>>     print("No API key found - please configure one")
        >>>     # Handle missing key scenario
    """
    # Preferred option: Check environment variable
    api_key = os.getenv('DEHASHED_API_KEY')
    if api_key:
        return api_key

    # Fallback option: Check config.ini
    config = ConfigParser()
    try:
        config.read('config.ini')
        return config.get('DEFAULT', 'DEHASHED_API_KEY')
    except (NoSectionError, NoOptionError, FileNotFoundError):
        return None


def get_api_email():
    """
    Retrieve DeHashed API email from secure storage locations.
    
    Attempts to retrieve the API email using multiple secure methods with
    priority given to environment variables for enhanced security.
    
    Search Order:
    1. DEHASHED_EMAIL environment variable (preferred)
    2. config.ini file [DEFAULT] section (fallback)
    
    Returns:
        str or None: The API email if found, None if no email is available
        
    Raises:
        No exceptions are raised; errors are handled gracefully
        
    Example:
        >>> email = get_api_email()
        >>> if email:
        >>>     print("API email loaded successfully")
        >>> else:
        >>>     print("No API email found - please configure one")
    """
    # Preferred option: Check environment variable
    api_email = os.getenv('DEHASHED_EMAIL')
    if api_email:
        return api_email

    # Fallback option: Check config.ini
    config = ConfigParser()
    try:
        config.read('config.ini')
        return config.get('DEFAULT', 'DEHASHED_EMAIL')
    except (NoSectionError, NoOptionError, FileNotFoundError):
        return None


def get_api_credentials():
    """
    Retrieve both DeHashed API email and key as a tuple.
    
    Convenience function to get both credentials needed for DeHashed API
    authentication in a single call.
    
    Returns:
        tuple: (email, api_key) if both are found, (None, None) if either is missing
        
    Example:
        >>> email, api_key = get_api_credentials()
        >>> if email and api_key:
        >>>     print("Both credentials loaded successfully")
        >>> else:
        >>>     print("Missing credentials - please configure both email and API key")
    """
    email = get_api_email()
    api_key = get_api_key()
    
    if email and api_key:
        return email, api_key
    else:
        return None, None

