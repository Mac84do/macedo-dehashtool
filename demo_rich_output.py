#!/usr/bin/env python3
"""
Demo script to showcase Rich table formatting for dataframes.
"""

import pandas as pd
from result_extraction import print_dataframe_table, print_extraction_summary

def demo_rich_output():
    """Demonstrate the Rich table formatting functionality."""
    
    # Create sample dataframe with various types of data
    sample_data = {
        'email': [
            'john.doe@company.com',
            'admin@example.org', 
            'user123@demo.net',
            'test@secure-site.io',
            'guest@sample.co.uk'
        ],
        'password': [
            'abc123',  # Short password (red)
            'password123',  # Medium password (yellow) 
            'SuperSecurePassword2024!',  # Long password (green)
            'mypass',  # Very short (red)
            'medium_length_pass'  # Medium (yellow)
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    print("🎨 Rich Table Formatting Demo")
    print("=" * 50)
    
    # Show extraction summary
    print_extraction_summary(df, original_count=8)
    
    # Show the beautifully formatted table
    print_dataframe_table(df)
    
    print("\n✨ Features demonstrated:")
    print("  • Rich table with colored borders and headers")
    print("  • Alternating row styles for better readability")
    print("  • Email domain highlighting")
    print("  • Password strength color coding")
    print("  • Total record count display")
    print("  • Proper table title with record count")
    
if __name__ == "__main__":
    demo_rich_output()
