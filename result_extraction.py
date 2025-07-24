#!/usr/bin/env python3
"""
Result extraction module for Dehashed API responses.

This module provides functionality to parse JSON responses from the Dehashed API
and extract email and password information into a pandas DataFrame.
"""

import pandas as pd
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.text import Text


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
def test_extraction():
    """
    Test the extraction function with sample data.
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
        print("🧪 Test Results:")
        print_extraction_summary(df, original_count)
        
        if len(df) > 0:
            console = Console()
            console.print(f"\n[bold cyan]📋 Sample Data:[/bold cyan]")
            print_dataframe_table(df)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    # Run test when script is executed directly
    test_extraction()
