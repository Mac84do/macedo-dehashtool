import requests
import time
import json
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


def search(query: str, api_key: str, max_retries: int = 3) -> Dict[Any, Any]:
    """
    Search the DeHashed API with the given query.
    
    Args:
        query: The search query string
        api_key: The API key for authentication
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
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    
    retry_count = 0
    base_delay = 1  # Initial delay in seconds
    
    while retry_count <= max_retries:
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=(api_key, ""),  # Username = api_key, password = empty string
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
