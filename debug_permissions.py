#!/usr/bin/env python3
"""
Debug script to test file permission issues.
"""

import os
import pandas as pd
from datetime import datetime
import re

def test_file_creation():
    """Test file creation in various directories to identify permission issues."""
    
    print("=== Permission Debugging Test ===")
    
    # Test data
    df = pd.DataFrame({
        'email': ['test@example.com', 'user@test.com'],
        'password': ['password123', 'secret456']
    })
    
    # Test 1: Current directory
    print("\n1. Testing current directory...")
    try:
        df.to_csv('test_current.csv', index=False)
        print("✅ Current directory: SUCCESS")
        os.remove('test_current.csv')
    except Exception as e:
        print(f"❌ Current directory FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 2: Output directory
    print("\n2. Testing output directory...")
    output_dir = 'output'
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Directory creation: SUCCESS - {os.path.abspath(output_dir)}")
        
        test_file = f"{output_dir}/test_output.csv"
        df.to_csv(test_file, index=False)
        print("✅ File creation in output/: SUCCESS")
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Output directory FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Absolute path: {os.path.abspath(output_dir)}")
    
    # Test 3: Date-formatted filename (like the main script uses)
    print("\n3. Testing with date-formatted filename...")
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        search_value = "example.com"
        query = re.sub(r'[^a-zA-Z0-9._-]', '_', search_value)
        file_name = f"{output_dir}/{date_str}_{query}.csv"
        
        print(f"   Attempting to create: {file_name}")
        df.to_csv(file_name, index=False)
        print("✅ Date-formatted filename: SUCCESS")
        os.remove(file_name)
        
    except Exception as e:
        print(f"❌ Date-formatted filename FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Full path: {os.path.abspath(file_name)}")
    
    # Test 4: Home directory fallback
    print("\n4. Testing home directory fallback...")
    try:
        home_output_dir = os.path.expanduser('~/dehashed_output')
        os.makedirs(home_output_dir, exist_ok=True)
        print(f"✅ Home directory creation: SUCCESS - {home_output_dir}")
        
        test_file = f"{home_output_dir}/test_home.csv"
        df.to_csv(test_file, index=False)
        print("✅ File creation in home directory: SUCCESS")
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Home directory FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 5: Check current working directory and permissions
    print("\n5. Environment information...")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   User home directory: {os.path.expanduser('~')}")
    print(f"   Output directory exists: {os.path.exists('output')}")
    if os.path.exists('output'):
        print(f"   Output directory is writable: {os.access('output', os.W_OK)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_file_creation()
