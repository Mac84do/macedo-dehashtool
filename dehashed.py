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
    
    print(f"Debug: Formatted query: {formatted_query}")
    
    # Debug output
    print(f"Debug: Email provided: {email[:10] + '...' if len(email) > 10 else email}" if email else "Debug: No email provided")
    print(f"Debug: API key provided: {api_key[:10] + '...' if len(api_key) > 10 else api_key}" if api_key else "Debug: No API key provided")
    print(f"Debug: Query: {query}")
    print(f"Debug: URL: {url}")
    print(f"Debug: Using Dehashed-Api-Key header")
    
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
                try:
                    return response.json()
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
