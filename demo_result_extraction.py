#!/usr/bin/env python3
"""
Demonstration script for result extraction functionality.

This script shows how to use the extract_email_password_data function
to parse JSON responses and create pandas DataFrames.
"""

import json
from result_extraction import extract_email_password_data, print_extraction_summary


def demo_basic_extraction():
    """Demonstrate basic result extraction with sample data."""
    print("=" * 60)
    print("🎯 DEMO: Basic Result Extraction")
    print("=" * 60)
    
    # Sample JSON response that might come from the Dehashed API
    sample_response = {
        "success": True,
        "total": 6,
        "entries": [
            {
                "id": "1001",
                "email": "john.doe@company.com", 
                "password": "password123",
                "username": "johndoe",
                "domain": "company.com",
                "breach": "Company Data Breach 2023"
            },
            {
                "id": "1002",
                "email": "jane.smith@company.com",
                "password": "secretpass",
                "username": "jsmith", 
                "domain": "company.com",
                "breach": "Company Data Breach 2023"
            },
            {
                "id": "1003",
                "email": "admin@company.com",
                "password": None,  # This will be dropped
                "username": "admin",
                "domain": "company.com", 
                "breach": "Company Data Breach 2023"
            },
            {
                "id": "1004",
                "email": "",  # Empty email - will be dropped
                "password": "adminpass", 
                "username": "admin2",
                "domain": "company.com",
                "breach": "Company Data Breach 2023"
            },
            {
                "id": "1005",
                "email": "user@company.com",
                "password": "   ",  # Whitespace-only password - will be dropped
                "username": "user",
                "domain": "company.com",
                "breach": "Company Data Breach 2023"
            },
            {
                "id": "1006", 
                "email": "support@company.com",
                "password": "support2023",
                "username": "support",
                "domain": "company.com",
                "breach": "Company Data Breach 2023"
            }
        ]
    }
    
    print("Original API Response:")
    print(json.dumps(sample_response, indent=2))
    print()
    
    # Extract the data
    original_count = len(sample_response['entries'])
    df = extract_email_password_data(sample_response)
    
    # Show results
    print_extraction_summary(df, original_count)
    
    if len(df) > 0:
        print(f"\n📋 Extracted DataFrame:")
        print(df.to_string(index=False))
        print(f"\n💾 DataFrame Info:")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Data types:")
        for col in df.columns:
            print(f"     {col}: {df[col].dtype}")


def demo_edge_cases():
    """Demonstrate handling of edge cases."""
    print("\n" + "=" * 60)
    print("🧪 DEMO: Edge Cases")
    print("=" * 60)
    
    # Test with empty entries
    empty_response = {"entries": []}
    print("1. Empty entries list:")
    df_empty = extract_email_password_data(empty_response)
    print_extraction_summary(df_empty, 0)
    
    # Test with missing entries key
    print("\n2. Missing 'entries' key:")
    try:
        invalid_response = {"success": False, "message": "No entries found"}
        df_invalid = extract_email_password_data(invalid_response)
    except KeyError as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    # Test with non-list entries
    print("\n3. Non-list entries:")
    try:
        bad_response = {"entries": "not a list"}
        df_bad = extract_email_password_data(bad_response)
    except ValueError as e:
        print(f"   ✅ Correctly caught error: {e}")


def demo_real_world_scenario():
    """Demonstrate a more realistic scenario."""
    print("\n" + "=" * 60)
    print("🌐 DEMO: Real-world Scenario")
    print("=" * 60)
    
    # Simulate a typical search result
    realistic_response = {
        "success": True,
        "total": 4,
        "entries": [
            {
                "email": "marketing@targetcompany.com",
                "password": "Marketing2023!",
                "database_name": "breach_db_1",
                "username": "mkt_team"
            },
            {
                "email": "sales@targetcompany.com", 
                "password": "SalesRock$",
                "database_name": "breach_db_2",
                "username": "sales"
            },
            {
                "email": "hr@targetcompany.com",
                "password": "",  # Empty - will be filtered out
                "database_name": "breach_db_1", 
                "username": "hr_dept"
            },
            {
                "email": "ceo@targetcompany.com",
                "password": "CEO_P@ssw0rd",
                "database_name": "breach_db_3",
                "username": "ceo"
            }
        ]
    }
    
    print("Realistic API response received...")
    df = extract_email_password_data(realistic_response)
    print_extraction_summary(df, len(realistic_response['entries']))
    
    if len(df) > 0:
        print(f"\n📊 Final Results:")
        print(df.to_string(index=False))
        
        # Show some basic analysis
        print(f"\n📈 Quick Analysis:")
        print(f"   • Unique domains: {df['email'].str.split('@').str[1].nunique()}")
        print(f"   • Average password length: {df['password'].str.len().mean():.1f} characters")
        print(f"   • Passwords with special chars: {df['password'].str.contains('[!@#$%^&*]').sum()}")


if __name__ == "__main__":
    # Run all demonstrations
    demo_basic_extraction()
    demo_edge_cases() 
    demo_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("✅ All demonstrations completed!")
    print("=" * 60)
