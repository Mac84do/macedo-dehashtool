import requests
import time
import json
import base64
from typing import Dict, Any


class DeHashedError(Exception):
    """Base exception for DeHashed API errors."""
    pass


class DeHashedRateLimitError(DeHashedError):
    """Exception raised when rate limit is exceeded."""
    pass


class DeHashedAPIError(DeHashedError):
    """Exception raised for API errors."""
    pass


def extract_rate_limit_info(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Extract rate limit information from API response headers.
    
    Args:
        headers: Dictionary of HTTP response headers
        
    Returns:
        Dictionary containing rate limit information, or empty dict if not found
    """
    rate_limit_info = {}
    
    # Common rate limit headers that APIs use
    header_mappings = {
        'x-ratelimit-remaining': 'API Calls Remaining (Rate Limit)',
        'x-ratelimit-limit': 'Rate Limit per Period',
        'x-ratelimit-reset': 'Rate Limit Reset Time',
        'x-ratelimit-used': 'API Calls Used',
        'x-quota-remaining': 'Quota Remaining',
        'x-quota-limit': 'Quota Limit',
        'x-balance': 'Account Balance',
        'x-credits': 'Available Credits',
        'x-credits-remaining': 'Credits Remaining',
        'dehashed-balance': 'DeHashed Balance',
        'dehashed-credits': 'DeHashed Credits',
        'dehashed-ratelimit-remaining': 'DeHashed Rate Limit Remaining',
        'dehashed-ratelimit-limit': 'DeHashed Rate Limit',
        'ratelimit-remaining': 'API Calls Remaining (Rate Limit)',
        'ratelimit-limit': 'Rate Limit',
        'rate-limit-remaining': 'API Calls Remaining (Rate Limit)',
        'rate-limit-limit': 'Rate Limit',
        'balance': 'Account Balance',
        'credits': 'Available Credits'
    }
    
    # Check for rate limit headers (case-insensitive)
    for header_name, display_name in header_mappings.items():
        for actual_header, value in headers.items():
            if actual_header.lower() == header_name.lower():
                rate_limit_info[display_name] = value
                break
    
    # Special handling for reset time (convert timestamp if needed)
    if 'Rate Limit Reset Time' in rate_limit_info:
        reset_value = rate_limit_info['Rate Limit Reset Time']
        try:
            # If it's a Unix timestamp, convert to readable time
            import datetime
            timestamp = int(reset_value)
            if timestamp > 1000000000:  # Looks like a Unix timestamp
                reset_time = datetime.datetime.fromtimestamp(timestamp)
                rate_limit_info['Rate Limit Reset Time'] = reset_time.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            # Keep original value if conversion fails
            pass
    
    return rate_limit_info


def search(query: str, email: str, api_key: str, max_retries: int = 3) -> Dict[Any, Any]:
    """
    Search the DeHashed API with the given query.
    
    Args:
        query: The search query string
        email: The email address for authentication (username)
        api_key: The API key for authentication (password)
        max_retries: Maximum number of retry attempts for rate limiting
        
    Returns:
        Dictionary containing the API response
        
    Raises:
        DeHashedRateLimitError: When rate limit is exceeded and retries are exhausted
        DeHashedAPIError: For other API errors (non-200 status codes)
        DeHashedError: For other general errors
    """
    url = "https://api.dehashed.com/v2/search"
    
    headers = {
        "Dehashed-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    # For domain searches, try using the domain: prefix format
    if '@' not in query and '.' in query:  # Likely a domain
        formatted_query = f"domain:{query}"
    else:
        formatted_query = query
        
    payload = {
        "query": formatted_query, 
        "size": 10000,
        "page": 1  # Add pagination parameter
    }
    
    # Only show formatted query for transparency
    if formatted_query != query:
        print(f"🔍 Search query formatted as: {formatted_query}")
    
    retry_count = 0
    base_delay = 1  # Initial delay in seconds
    
    while retry_count <= max_retries:
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Handle rate limiting (HTTP 429)
            if response.status_code == 429:
                if retry_count >= max_retries:
                    raise DeHashedRateLimitError(
                        f"Rate limit exceeded. Max retries ({max_retries}) reached."
                    )
                
                # Get retry delay from Retry-After header, or use exponential backoff
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = int(retry_after)
                    except ValueError:
                        # If Retry-After is not a valid integer, use exponential backoff
                        delay = base_delay * (2 ** retry_count)
                else:
                    delay = base_delay * (2 ** retry_count)
                
                print(f"Rate limit hit. Retrying in {delay} seconds... (attempt {retry_count + 1}/{max_retries + 1})")
                time.sleep(delay)
                retry_count += 1
                continue
            
            # Handle successful response
            if response.status_code == 200:
                # Parse response to get balance info
                try:
                    response_data = response.json()
                    balance = response_data.get('balance')
                except:
                    response_data = {}
                    balance = None
                
                # Extract and display rate limit information from headers
                rate_limit_info = extract_rate_limit_info(response.headers)
                
                print(f"\n📊 API Usage Information:")
                
                # Display account balance/credits if available
                if balance is not None:
                    print(f"   💳 Account Credits: {balance}")
                
                # Display rate limit info
                if rate_limit_info:
                    # Display the most important info first (remaining calls)
                    if 'API Calls Remaining (Rate Limit)' in rate_limit_info:
                        remaining = rate_limit_info['API Calls Remaining (Rate Limit)']
                        total = rate_limit_info.get('Rate Limit per Period', 'Unknown')
                        print(f"   🔄 Rate Limit: {remaining}/{total} (per period)")
                    
                    # Display other rate limit info
                    for key, value in rate_limit_info.items():
                        if key not in ['API Calls Remaining (Rate Limit)', 'Rate Limit per Period']:
                            print(f"   {key}: {value}")
                
                print()  # Empty line for better readability
                
                try:
                    return response_data if response_data else response.json()
                except json.JSONDecodeError as e:
                    raise DeHashedError(f"Failed to parse JSON response: {e}")
            
            # Handle other HTTP errors
            error_message = f"API request failed with status {response.status_code}"
            
            # Try to get error details from response body
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_message += f": {error_data['message']}"
                elif "error" in error_data:
                    error_message += f": {error_data['error']}"
            except (json.JSONDecodeError, KeyError):
                # If we can't parse the error response, include the raw text
                if response.text:
                    error_message += f": {response.text[:200]}"
            
            raise DeHashedAPIError(error_message)
            
        except requests.exceptions.RequestException as e:
            raise DeHashedError(f"Network error occurred: {e}")
        except Exception as e:
            if isinstance(e, (DeHashedError, DeHashedRateLimitError, DeHashedAPIError)):
                raise
            raise DeHashedError(f"Unexpected error occurred: {e}")
