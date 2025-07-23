import os
from configparser import ConfigParser, NoSectionError, NoOptionError

def get_api_key():
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

