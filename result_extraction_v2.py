#!/usr/bin/env python3
"""
Result extraction module for Dehashed API responses (v2) - Enhanced Dynamic Data-Extraction Engine.

This module provides functionality to parse JSON responses from the Dehashed API
and extract data into pandas DataFrames with intelligent field detection and sanitization.

Features:
- Parse api_response["entries"] into pandas DataFrame via pd.json_normalize, capturing all nested keys
- Guarantee presence of commonly-expected columns (email, password, username, etc.)
- Utility functions for field extraction and summarization
- Column sanitization (flatten dotted keys, replace spaces with underscores)
- Intelligent duplicate and empty row removal
- Hash column detection for cracking phases
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text


# ================================
# ENHANCED DYNAMIC DATA EXTRACTION ENGINE
# ================================

def _sanitize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitize column names by flattening dotted keys and replacing spaces with underscores.
    
    Args:
        df: DataFrame with potentially messy column names
        
    Returns:
        DataFrame with sanitized column names
    """
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Sanitize column names
    new_columns = []
    for col in df_copy.columns:
        # Replace dots with underscores (flatten nested keys)
        sanitized = col.replace('.', '_')
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Replace multiple underscores with single underscore
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Convert to lowercase for consistency
        sanitized = sanitized.lower()
        new_columns.append(sanitized)
    
    df_copy.columns = new_columns
    return df_copy


def _ensure_common_columns(df: pd.DataFrame, common_cols: List[str]) -> pd.DataFrame:
    """
    Ensure presence of commonly-expected columns by adding them if missing.
    
    Args:
        df: DataFrame to check
        common_cols: List of column names that should exist
        
    Returns:
        DataFrame with guaranteed columns
    """
    df_copy = df.copy()
    for column in common_cols:
        if column not in df_copy.columns:
            df_copy[column] = None  # Default to None if column is missing
    return df_copy


def _detect_hash_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect columns that likely contain hashes based on naming patterns and data characteristics.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        List of column names that likely contain hashes
    """
    hash_columns = []
    
    # Common hash field names
    hash_patterns = [
        r'.*hash.*',
        r'.*md5.*',
        r'.*sha.*',
        r'.*bcrypt.*',
        r'.*scrypt.*',
        r'.*pbkdf2.*',
        r'.*ntlm.*',
        r'.*lm.*',
        r'.*crypt.*'
    ]
    
    for column in df.columns:
        column_lower = column.lower()
        
        # Check naming patterns
        for pattern in hash_patterns:
            if re.match(pattern, column_lower):
                hash_columns.append(column)
                break
        
        # Check data characteristics (if not already matched by name)
        if column not in hash_columns and not df[column].empty:
            # Sample some non-null values
            sample_values = df[column].dropna().astype(str).head(10)
            if len(sample_values) > 0:
                # Check for hex patterns (common in hashes)
                hex_pattern_count = 0
                for value in sample_values:
                    # Check if value looks like a hash (hex string of typical hash lengths)
                    if re.match(r'^[a-fA-F0-9]{16,}$', value) and len(value) in [32, 40, 56, 64, 96, 128]:
                        hex_pattern_count += 1
                
                # If majority of sampled values look like hashes, consider it a hash column
                if hex_pattern_count >= len(sample_values) * 0.7:
                    hash_columns.append(column)
    
    return hash_columns


def _intelligent_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Intelligently remove duplicates and empty rows.
    
    Args:
        df: DataFrame to clean
        
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
        
    df_copy = df.copy()
    
    # Remove completely empty rows (all values are NaN)
    df_copy = df_copy.dropna(how='all')
    
    # Remove exact duplicates
    df_copy = df_copy.drop_duplicates()
    
    # Reset index
    df_copy = df_copy.reset_index(drop=True)
    
    return df_copy


def extract_all_fields(api_response: Dict[Any, Any]) -> pd.DataFrame:
    """
    Parse api_response["entries"] into a pandas DataFrame via pd.json_normalize,
    automatically capturing all nested keys with intelligent processing.
    
    Args:
        api_response: Dictionary containing the Dehashed API response
        
    Returns:
        pandas.DataFrame: DataFrame with all fields from entries, sanitized and cleaned
    """
    if 'entries' not in api_response:
        raise KeyError("'entries' key not found in API response")
    
    entries = api_response['entries']
    if not isinstance(entries, list):
        raise ValueError("'entries' must be a list")
    
    if not entries:  # Empty list
        return pd.DataFrame()
    
    # Use pd.json_normalize to capture all nested keys
    df = pd.json_normalize(entries)
    
    # Sanitize column names
    df = _sanitize_column_names(df)
    
    # Ensure common columns exist
    common_cols = ['email', 'password', 'username', 'domain', 'id', 'name', 'phone', 'address']
    df = _ensure_common_columns(df, common_cols)
    
    # Intelligent cleanup
    df = _intelligent_cleanup(df)
    
    return df


def summarize_fields(df: pd.DataFrame) -> None:
    """
    Print counts and unique values per column using Rich formatting.
    
    Args:
        df: DataFrame to summarize
    """
    console = Console()
    
    if df.empty:
        console.print("[bold red]No data to summarize[/bold red]")
        return
    
    console.print(f"\n[bold blue]📊 Field Summary ({len(df)} total records):[/bold blue]")
    
    # Create Rich table
    table = Table(
        title="[bold green]Column Analysis[/bold green]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        row_styles=["none", "dim"]
    )
    
    table.add_column("Column Name", style="bold white", justify="left")
    table.add_column("Non-Null Count", justify="right", style="green")
    table.add_column("Unique Values", justify="right", style="cyan")
    table.add_column("Data Type", justify="center", style="yellow")
    table.add_column("Sample Value", justify="left", style="dim white", no_wrap=False)
    
    for column in df.columns:
        non_null_count = len(df[column].dropna())
        unique_count = df[column].nunique()
        data_type = str(df[column].dtype)
        
        # Get a sample non-null value
        sample_values = df[column].dropna()
        if len(sample_values) > 0:
            sample_value = str(sample_values.iloc[0])
            # Truncate if too long
            if len(sample_value) > 50:
                sample_value = sample_value[:47] + "..."
        else:
            sample_value = "[dim red]<no data>[/dim red]"
        
        table.add_row(
            column,
            str(non_null_count),
            str(unique_count),
            data_type,
            sample_value
        )
    
    console.print(table)
    
    # Additional statistics
    console.print(f"\n[bold]Summary Statistics:[/bold]")
    console.print(f"   • [green]Total columns:[/green] {len(df.columns)}")
    console.print(f"   • [cyan]Total rows:[/cyan] {len(df)}")
    console.print(f"   • [yellow]Memory usage:[/yellow] {df.memory_usage(deep=True).sum() / 1024:.1f} KB")


def list_hash_columns(df: pd.DataFrame) -> List[str]:
    """
    Export helper to list detected hash columns for later cracking phase.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        List of column names that likely contain hashes
    """
    hash_cols = _detect_hash_columns(df)
    
    if hash_cols:
        console = Console()
        console.print(f"\n[bold yellow]🔐 Detected Hash Columns ({len(hash_cols)} found):[/bold yellow]")
        for col in hash_cols:
            # Show sample hash values
            sample_hashes = df[col].dropna().head(3).tolist()
            console.print(f"   • [cyan]{col}[/cyan]: {', '.join(str(h)[:20] + '...' if len(str(h)) > 20 else str(h) for h in sample_hashes)}")
    
    return hash_cols


# ================================
# LEGACY FUNCTIONS (maintained for backward compatibility)
# ================================

def extract_email_password_data(api_response: Dict[Any, Any]) -> pd.DataFrame:
    """
    Extract email and password data from DeHashed API response.
    Handles multiple data formats:
    1. password field as list with email;password format
    2. separate email and password fields (both as lists or strings)
    3. entries with only email but no password

    Args:
        api_response: Dictionary containing the Dehashed API response

    Returns:
        pandas.DataFrame: DataFrame with 'email' and 'password' columns
    """
    if 'entries' not in api_response:
        raise KeyError("'entries' key not found in API response")

    entries = api_response['entries']
    if not isinstance(entries, list):
        raise ValueError("'entries' must be a list")

    extracted_data = []

    for entry in entries:
        # Method 1: password field contains email;password format
        if 'password' in entry:
            password_data = entry['password']
            if isinstance(password_data, list):
                for p in password_data:
                    if ';' in str(p):
                        email_pass = str(p).split(';')
                        if len(email_pass) == 2:
                            extracted_data.append({
                                'email': email_pass[0].strip(),
                                'password': email_pass[1].strip()
                            })
                    # Method 2: password is just the password, get email from email field
                    elif 'email' in entry:
                        email_data = entry['email']
                        emails = email_data if isinstance(email_data, list) else [email_data]
                        for email in emails:
                            if email:  # Skip None/empty emails
                                extracted_data.append({
                                    'email': str(email).strip(),
                                    'password': str(p).strip()
                                })
            elif isinstance(password_data, str) and 'email' in entry:
                # Single password string with separate email field
                email_data = entry['email']
                emails = email_data if isinstance(email_data, list) else [email_data]
                for email in emails:
                    if email:  # Skip None/empty emails
                        extracted_data.append({
                            'email': str(email).strip(),
                            'password': str(password_data).strip()
                        })

    df = pd.DataFrame(extracted_data)

    if df.empty:
        return pd.DataFrame(columns=['email', 'password'])

    # Remove duplicates
    df = df.drop_duplicates()

    # Drop rows with null/empty values
    df_cleaned = df.dropna(subset=['email', 'password'])
    df_cleaned = df_cleaned[
        (df_cleaned['email'].str.strip() != '') & 
        (df_cleaned['password'].str.strip() != '')
    ]

    df_cleaned = df_cleaned.reset_index(drop=True)
    return df_cleaned


def print_dataframe_table(df: pd.DataFrame) -> None:
    """
    Pretty-print a DataFrame using Rich table formatting with syntax highlighting.
    
    Args:
        df: The pandas DataFrame to display
    """
    console = Console()
    
    if df.empty:
        console.print("[bold red]No data to display[/bold red]")
        return
    
    # Create Rich table
    table = Table(
        title=f"[bold green]Extracted Data ({len(df)} records)[/bold green]",
        title_justify="left",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        row_styles=["none", "dim"]
    )
    
    # Add columns
    table.add_column("Email", style="blue", justify="left", no_wrap=False)
    table.add_column("Password", style="yellow", justify="left", no_wrap=False)
    
    # Add rows with syntax highlighting for email domains
    for _, row in df.iterrows():
        email = str(row['email'])
        password = str(row['password'])
        
        # Highlight email domain in cyan
        if '@' in email:
            username, domain = email.split('@', 1)
            formatted_email = f"{username}@[cyan]{domain}[/cyan]"
        else:
            formatted_email = email
        
        # Add some visual indicators for password strength (basic)
        if len(password) >= 12:
            password_style = f"[green]{password}[/green]"
        elif len(password) >= 8:
            password_style = f"[yellow]{password}[/yellow]"
        else:
            password_style = f"[red]{password}[/red]"
        
        table.add_row(formatted_email, password_style)
    
    # Print the table
    console.print()
    console.print(table)
    console.print(f"\n[bold]Total Records:[/bold] [cyan]{len(df)}[/cyan]")


def print_extraction_summary(df: pd.DataFrame, original_count: int = None) -> None:
    """
    Print a summary of the extraction results using Rich formatting.
    
    Args:
        df: The cleaned DataFrame
        original_count: Optional count of original entries before cleaning
    """
    console = Console()
    
    console.print("\n[bold blue]📊 Extraction Summary:[/bold blue]")
    console.print(f"   • [green]Final records:[/green] [bold cyan]{len(df)}[/bold cyan]")
    
    if original_count is not None:
        dropped_count = original_count - len(df)
        console.print(f"   • [yellow]Original entries:[/yellow] {original_count}")
        console.print(f"   • [red]Dropped (null/empty):[/red] {dropped_count}")
    
    if len(df) > 0:
        console.print(f"   • [magenta]Unique emails:[/magenta] {df['email'].nunique()}")
        console.print(f"   • [cyan]Unique passwords:[/cyan] {df['password'].nunique()}")
    else:
        console.print("   • [bold red]No valid email/password pairs found[/bold red]")


# Example usage and testing function
def test_extraction_v2():
    """
    Test the extraction function with sample data (v2).
    """
    # Sample API response for testing
    sample_response = {
        "success": True,
        "total": 5,
        "entries": [
            {
                "id": "1",
                "email": "user1@example.com",
                "password": "password123",
                "username": "user1",
                "domain": "example.com"
            },
            {
                "id": "2", 
                "email": "user2@example.com",
                "password": "",  # Empty password - should be dropped
                "username": "user2",
                "domain": "example.com"
            },
            {
                "id": "3",
                "email": None,  # Null email - should be dropped
                "password": "password456",
                "username": "user3",
                "domain": "example.com"
            },
            {
                "id": "4",
                "email": "user4@example.com",
                "password": "password789",
                "username": "user4",
                "domain": "example.com"
            },
            {
                "id": "5",
                "email": "   ",  # Whitespace-only email - should be dropped
                "password": "password000",
                "username": "user5",
                "domain": "example.com"
            }
        ]
    }
    
    try:
        # Extract data
        original_count = len(sample_response['entries'])
        df = extract_email_password_data(sample_response)
        
        # Print results
        print("🧪 Test Results (v2):")
        print_extraction_summary(df, original_count)
        
        if len(df) > 0:
            console = Console()
            console.print(f"\n[bold cyan]📋 Sample Data:[/bold cyan]")
            print_dataframe_table(df)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_enhanced_extraction():
    """
    Test the enhanced extraction functions with comprehensive sample data.
    """
    console = Console()
    console.print("\n[bold blue]🧪 Testing Enhanced Dynamic Data-Extraction Engine[/bold blue]")
    
    # Sample API response with nested data and various field types
    enhanced_sample_response = {
        "success": True,
        "total": 8,
        "entries": [
            {
                "id": "1",
                "email": "john.doe@company.com",
                "password": "mypassword123",
                "username": "johndoe",
                "domain": "company.com",
                "user.profile.name": "John Doe",  # Nested key to test flattening
                "phone": "+1-555-0123",
                "md5_hash": "5d41402abc4b2a76b9719d911017c592",
                "registration_date": "2023-01-15"
            },
            {
                "id": "2",
                "email": "jane.smith@example.org",
                "password": "securepass456",
                "username": "janesmith",
                "domain": "example.org",
                "user profile name": "Jane Smith",  # Space in key name
                "phone": "+1-555-0456",
                "sha256_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
                "registration_date": "2023-02-20"
            },
            {
                "id": "3",
                "email": "bob.wilson@test.net",
                "password": "bobspassword",
                "username": "bobwilson",
                "domain": "test.net",
                "user.profile.name": "Bob Wilson",
                "address": {  # Nested object
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345"
                },
                "bcrypt_hash": "$2a$10$N9qo8uLOickgx2ZMRZoMye"
            },
            {
                "id": "4",
                "email": "",  # Empty email
                "password": "shouldbedropped",
                "username": "emptyemail",
                "domain": "nowhere.com"
            },
            {
                "id": "5",
                "email": "alice@secure.gov",
                "password": None,  # Null password
                "username": "alice",
                "domain": "secure.gov",
                "phone": "+1-555-0789"
            },
            {
                "id": "6",
                "email": "duplicate@test.com",
                "password": "duplicate123",
                "username": "duplicate1",
                "domain": "test.com"
            },
            {
                "id": "7",
                "email": "duplicate@test.com",  # Duplicate entry
                "password": "duplicate123",
                "username": "duplicate2",
                "domain": "test.com"
            },
            {
                "id": "8",
                "email": "complete@example.com",
                "password": "completeuserdata",
                "username": "complete",
                "domain": "example.com",
                "name": "Complete User",
                "phone": "+1-555-9999",
                "address": "789 Complete Ave",
                "ntlm_hash": "aad3b435b51404eeaad3b435b51404ee"
            }
        ]
    }
    
    try:
        console.print("\n[bold yellow]🔧 Testing extract_all_fields() function...[/bold yellow]")
        
        # Test the new enhanced extraction function
        df_all = extract_all_fields(enhanced_sample_response)
        
        console.print(f"[green]✅ Successfully extracted {len(df_all)} records with {len(df_all.columns)} columns[/green]")
        
        # Show column sanitization results
        console.print("\n[bold cyan]📋 Column names after sanitization:[/bold cyan]")
        for i, col in enumerate(df_all.columns, 1):
            console.print(f"   {i:2d}. [cyan]{col}[/cyan]")
        
        # Test summarize_fields function
        console.print("\n[bold yellow]🔧 Testing summarize_fields() function...[/bold yellow]")
        summarize_fields(df_all)
        
        # Test hash column detection
        console.print("\n[bold yellow]🔧 Testing list_hash_columns() function...[/bold yellow]")
        hash_cols = list_hash_columns(df_all)
        
        if not hash_cols:
            console.print("[yellow]ℹ️  No hash columns detected in this dataset[/yellow]")
        
        # Compare with legacy function
        console.print("\n[bold yellow]🔧 Comparing with legacy extract_email_password_data()...[/bold yellow]")
        df_legacy = extract_email_password_data(enhanced_sample_response)
        
        console.print(f"[green]Enhanced function:[/green] {len(df_all)} records, {len(df_all.columns)} columns")
        console.print(f"[yellow]Legacy function:[/yellow] {len(df_legacy)} records, {len(df_legacy.columns)} columns")
        
        # Show sample of enhanced data
        if len(df_all) > 0:
            console.print("\n[bold magenta]📊 Sample of Enhanced Extraction (first 3 records):[/bold magenta]")
            sample_df = df_all.head(3)
            
            # Create a detailed table showing more columns
            table = Table(
                title="Enhanced Data Sample",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            
            # Add key columns to display
            display_cols = ['id', 'email', 'username', 'domain']
            for col in display_cols:
                if col in sample_df.columns:
                    table.add_column(col.title(), style="white")
            
            for _, row in sample_df.iterrows():
                row_data = []
                for col in display_cols:
                    if col in sample_df.columns:
                        value = str(row[col]) if row[col] is not None else "[dim]None[/dim]"
                        row_data.append(value)
                table.add_row(*row_data)
            
            console.print(table)
        
        console.print("\n[bold green]🎉 All enhanced extraction tests completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Enhanced extraction test failed: {e}[/bold red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")


if __name__ == "__main__":
    # Run both legacy and enhanced tests when script is executed directly
    test_extraction_v2()
    test_enhanced_extraction()
