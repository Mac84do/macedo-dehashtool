#!/usr/bin/env python3
"""
Main CLI application for Dehashed API tool (v2).

Provides an interactive interface for domain and email searches.
"""

import sys
import os
import re
from time import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from get_api_key import get_api_credentials
from dehashed import search, DeHashedError, DeHashedRateLimitError, DeHashedAPIError
from result_extraction_v2 import extract_email_password_data, print_extraction_summary, print_dataframe_table, extract_all_fields, list_hash_columns
from pdf_generator_v2 import generate_pdf_report, create_pdf_from_dataframe_v2
from hash_cracking import detect_tools, choose_tool, get_hash_type, get_wordlist, spawn_cracking_tool, capture_output, parse_output
import tempfile
import pandas as pd
from typing import Dict, Any, List, Optional

# Initialize Rich console
console = Console()

def print_welcome_banner():
    """
    Display a formatted welcome banner using Rich console formatting.
    
    Creates an attractive terminal banner with the application title,
    description, and branding using Rich Panel and Text components.
    The banner includes:
    - Application title with cyan styling
    - Welcome message and purpose description
    - Decorative heart emoji for branding
    - Cyan border styling with proper padding
    
    Returns:
        None: Prints directly to console
        
    Example:
        >>> print_welcome_banner()
        # Displays formatted banner to terminal
    """
    title = Text("Dehashed API Tool V2", style="bold cyan")
    banner_text = Text.assemble(
        "Welcome to the ", ("Dehashed", "bold blue"), " API search tool!\n",
        "Search for compromised credentials by domain or email address.\n",
        "Built with ❤️  for security research."
    )
    
    banner = Panel(
        banner_text,
        title=title,
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(banner)
    console.print()

def get_search_choice():
    """
    Prompt the user to select between domain or email search.
    
    Displays search options and validates user input using Rich prompts.
    Only accepts valid choices ("1" for domain, "2" for email).
    Defaults to domain search if no selection is made.
    
    Returns:
        str: User's choice ("1" for domain search, "2" for email search)
        
    Example:
        >>> choice = get_search_choice()
        >>> if choice == "1":
        >>>     print("Domain search selected")
        >>> else:
        >>>     print("Email search selected")
    """
    console.print("[bold]Search Options:[/bold]")
    console.print("1) Domain search")
    console.print("2) Email search")
    console.print()
    
    while True:
        choice = Prompt.ask(
            "Select search type",
            choices=["1", "2"],
            default="1"
        )
        return choice

def get_search_value(search_type):
    """
    Prompt the user to enter their search query based on selected type.
    
    Displays appropriate prompt text and examples based on whether the user
    selected domain or email search. Provides helpful examples to guide
    user input formatting.
    
    Args:
        search_type (str): The search type ("1" for domain, "2" for email)
        
    Returns:
        str: The search value entered by the user, stripped of whitespace
        
    Example:
        >>> search_value = get_search_value("1")
        # Prompts: "Enter domain to search (e.g., example.com)"
        >>> search_value = get_search_value("2")
        # Prompts: "Enter email address to search (e.g., user@example.com)"
    """
    if search_type == "1":
        prompt_text = "Enter domain to search"
        example = " (e.g., example.com)"
    else:
        prompt_text = "Enter email address to search"
        example = " (e.g., user@example.com)"
    
    console.print()
    value = Prompt.ask(f"[bold]{prompt_text}[/bold]{example}")
    return value.strip()

def confirm_search(search_type, search_value):
    """
    Display search summary and get user confirmation before API call.
    
    Shows a formatted summary of the planned search including type and value,
    then prompts for confirmation. This prevents accidental API calls and
    allows users to verify their input before consuming API quota.
    
    Args:
        search_type (str): The search type ("1" for domain, "2" for email)
        search_value (str): The search query string entered by user
        
    Returns:
        bool: True if user confirms, False if they cancel
        
    Example:
        >>> confirmed = confirm_search("1", "example.com")
        >>> if confirmed:
        >>>     # Proceed with API search
        >>>     pass
    """
    search_type_name = "Domain" if search_type == "1" else "Email"
    
    console.print()
    console.print(f"[bold]Search Summary:[/bold]")
    console.print(f"Type: {search_type_name} search")
    console.print(f"Value: [cyan]{search_value}[/cyan]")
    console.print()
    
    return Confirm.ask("Proceed with API search?", default=True)

def perform_api_search(search_type, search_value, email, api_key):
    """
    Execute the DeHashed API search and process results.
    
    Sends a search query to the DeHashed API using provided search type
    and value along with user's API key. Handles response extraction,
    data cleaning, and output generation including CSV and PDF files.
    
    Args:
        search_type (str): The search type ("1" for domain, "2" for email)
        search_value (str): The search query string entered by user
        email (str): User's email for authentication
        api_key (str): User's API key for authentication
        
    Returns:
        None: Operates with side effects like creating files and
              printing to the console
    
    Raises:
        DeHashedRateLimitError: When rate limit is hit
        DeHashedAPIError: For unexpected API errors
        DeHashedError: For general errors affecting search
        
    Example:
        >>> perform_api_search("1", "example.com", "your_api_key")
        # Outputs
        ✅ Dataframe saved to output/2025-01-23_example.com.csv
        ✅ PDF report saved to output/2025-01-23_example.com.pdf
    """
    search_type_name = "domain" if search_type == "1" else "email"

    console.print(f"[yellow]Searching Dehashed API for {search_type_name}: {search_value}...[/yellow]")

    try:
        # Perform the search
        response = search(query=search_value, email=email, api_key=api_key)
        
        # Debug: Print raw response info
        print(f"Debug: Raw response keys: {list(response.keys())}")
        entries = response.get('entries', [])
        print(f"Debug: Number of entries: {len(entries)}")
        print(f"Debug: Total in response: {response.get('total', 'N/A')}")
        
        if entries and len(entries) > 0:
            print(f"Debug: First entry keys: {list(entries[0].keys())}")
            print(f"Debug: First entry sample: {entries[0]}")
            
            # Check if there are different structures in other entries
            for i, entry in enumerate(entries[:5]):  # Check first 5 entries
                print(f"Debug: Entry {i} keys: {list(entry.keys())}")
                if 'email' in entry:
                    print(f"Debug: Entry {i} has email field: {entry.get('email')}")
                if 'username' in entry:
                    print(f"Debug: Entry {i} has username field: {entry.get('username')}")
                if 'domain' in entry:
                    print(f"Debug: Entry {i} has domain field: {entry.get('domain')}")
        
        # Extract results
        original_count = len(entries)
        df = extract_email_password_data(response)

        # Print results
        print_extraction_summary(df, original_count)

        if len(df) > 0:
            print_dataframe_table(df)
            
            # Save the dataframe to a CSV file
            # Get current date and time
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Create output directory if it doesn't exist
            output_dir = 'output'
            try:
                os.makedirs(output_dir, exist_ok=True)
                
                # On Windows, set full permissions to avoid Errno 13 issues
                if os.name == 'nt':  # Windows
                    try:
                        import stat
                        os.chmod(output_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        console.print(f"[green]Set full permissions on output directory[/green]")
                    except Exception as chmod_e:
                        console.print(f"[yellow]Warning: Could not set directory permissions: {chmod_e}[/yellow]")
                
                console.print(f"[green]Using output directory: {os.path.abspath(output_dir)}[/green]")
            except PermissionError as e:
                console.print(f"[red]Permission denied creating directory: {os.path.abspath(output_dir)}[/red]")
                console.print(f"[red]Error details: {str(e)}[/red]")
                # Fallback to user's home directory if permission denied
                output_dir = os.path.expanduser('~/dehashed_output')
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    # Set permissions on fallback directory too
                    if os.name == 'nt':  # Windows
                        try:
                            import stat
                            os.chmod(output_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        except Exception:
                            pass  # Ignore chmod errors on fallback
                    console.print(f"[yellow]Warning: Using fallback directory {output_dir} due to permissions[/yellow]")
                except Exception as fallback_e:
                    console.print(f"[red]Failed to create fallback directory: {str(fallback_e)}[/red]")
                    return
            except Exception as e:
                console.print(f"[red]Unexpected error creating output directory: {str(e)}[/red]")
                console.print(f"[red]Error type: {type(e).__name__}[/red]")
                return
            
            # Create file name
            # Sanitize query for filename (replace spaces and special characters)
            query = re.sub(r'[^a-zA-Z0-9._-]', '_', search_value)
            file_name = f"{output_dir}/{date_str}_{query}.csv"
            
            # Save to CSV
            console.print(f"[cyan]Attempting to save to: {file_name}[/cyan]")
            console.print(f"[cyan]File exists: {os.path.exists(file_name)}[/cyan]")
            console.print(f"[cyan]Directory writable: {os.access(os.path.dirname(file_name), os.W_OK)}[/cyan]")
            
            try:
                # Check if file is locked by another process
                if os.path.exists(file_name):
                    try:
                        # Try to open in append mode to check if it's locked
                        with open(file_name, 'a'):
                            pass
                        console.print(f"[cyan]File not locked, proceeding...[/cyan]")
                    except PermissionError:
                        console.print(f"[yellow]File appears to be locked, will try to overwrite...[/yellow]")
                
                df.to_csv(file_name, index=False)
                console.print(f"[green]✅ Dataframe saved to {file_name}[/green]")
            except PermissionError as e:
                console.print(f"[red]❌ Permission denied writing to {file_name}[/red]")
                console.print(f"[red]Error details: {str(e)}[/red]")
                # Try alternative location
                home_output_dir = os.path.expanduser('~/dehashed_output')
                os.makedirs(home_output_dir, exist_ok=True)
                # Set permissions on alternative directory
                if os.name == 'nt':  # Windows
                    try:
                        import stat
                        os.chmod(home_output_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception:
                        pass  # Ignore chmod errors
                alt_file_name = file_name.replace(output_dir, home_output_dir)
                console.print(f"[yellow]Trying alternative location: {alt_file_name}[/yellow]")
                try:
                    df.to_csv(alt_file_name, index=False)
                    console.print(f"[green]✅ Dataframe saved to {alt_file_name}[/green]")
                    file_name = alt_file_name  # Update for PDF generation
                except Exception as alt_e:
                    console.print(f"[red]❌ Failed to save to alternative location: {str(alt_e)}[/red]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Unexpected error saving CSV: {str(e)}[/red]")
                console.print(f"[red]Error type: {type(e).__name__}[/red]")
                return
            
            # Generate PDF report
            try:
                pdf_path = generate_pdf_report(file_name)
                console.print(f"[green]✅ PDF report saved to {pdf_path}[/green]")
            except ImportError as e:
                if 'reportlab' in str(e):
                    console.print(f"[yellow]⚠️  PDF generation skipped: reportlab not installed[/yellow]")
                    console.print(f"[yellow]💡 Install with: pip install reportlab[/yellow]")
                else:
                    console.print(f"[yellow]⚠️  PDF generation failed: missing dependency {e}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  PDF generation failed: {str(e)}[/yellow]")
            
            # Post-processing options
            console.print("\n[bold cyan]🔧 Post-Processing Options[/bold cyan]")
            
            # Check for hashes
            hash_columns = list_hash_columns(df)
            
            # Check for passwords (for analysis)
            password_count = 0
            if 'password' in df.columns:
                password_count = df[df['password'].notna() & (df['password'] != '')].shape[0]
            
            # Display what we found
            if hash_columns:
                console.print(f"[yellow]🔐 Found {len(hash_columns)} hash column(s) with potential hashes to crack[/yellow]")
            if password_count > 0:
                console.print(f"[green]🔑 Found {password_count} plaintext password(s) for analysis[/green]")
            
            # Always ask about post-processing if we have any credentials
            if hash_columns or password_count > 0:
                # Hash cracking option
                if hash_columns:
                    hash_confirm = Confirm.ask("\n🔐 Do you want to attempt to crack the detected hashes?", default=False)
                    if hash_confirm:
                        cracked_results = perform_hash_cracking(df, hash_columns)
                        if cracked_results is not None:
                            df = df.merge(cracked_results, on=list(cracked_results.columns.drop('plaintext_password')), how='left')
                            
                            # Save cracked results
                            cracked_file_name = file_name.replace('.csv', '_cracked.csv')
                            df.to_csv(cracked_file_name, index=False)
                            console.print(f"[green]✅ Cracked results saved to {cracked_file_name}[/green]")

                            # Generate updated PDF
                            try:
                                hash_cracking_data = {
                                    'hashes_attempted': len(cracked_results),
                                    'hashes_cracked': cracked_results['plaintext_password'].notnull().sum()
                                }
                                pdf_path = create_pdf_from_dataframe_v2(
                                    df,
                                    query,
                                    hash_crack_results=hash_cracking_data,
                                    output_pdf_path=file_name.replace('.csv', '.pdf')
                                )
                                console.print(f"[green]✅ Updated PDF report saved to {pdf_path}[/green]")
                            except Exception as e:
                                console.print(f"[yellow]⚠️  Failed to update PDF report: {str(e)}[/yellow]")
                
                # Password analysis option
                if password_count > 0:
                    analysis_confirm = Confirm.ask("\n📊 Do you want to perform password analysis (common patterns, weak passwords)?", default=False)
                    if analysis_confirm:
                        perform_password_analysis(df, file_name)
                
                # Additional options
                console.print("\n[cyan]Additional Options:[/cyan]")
                if Confirm.ask("🔍 Generate detailed field summary report?", default=False):
                    generate_field_summary_report(df, file_name)
            else:
                console.print("[yellow]ℹ️  No credentials found for post-processing[/yellow]")
            return True
        else:
            console.print("[bold red]No valid email/password pairs found.[/bold red]")
            return False

    except (DeHashedRateLimitError, DeHashedAPIError, DeHashedError) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return False

def perform_password_analysis(df: pd.DataFrame, file_name: str) -> None:
    """
    Perform password analysis to identify common patterns and weak passwords.
    
    Args:
        df: DataFrame containing password data
        file_name: Base file name for saving analysis results
    """
    console.print("\n[bold cyan]📊 Password Analysis[/bold cyan]")
    
    if 'password' not in df.columns:
        console.print("[red]No password column found for analysis[/red]")
        return
    
    passwords = df[df['password'].notna() & (df['password'] != '')]['password']
    
    if len(passwords) == 0:
        console.print("[red]No passwords found for analysis[/red]")
        return
    
    # Password strength analysis
    weak_passwords = []
    common_patterns = {
        'contains_name': 0,
        'contains_year': 0,
        'simple_pattern': 0,
        'short_length': 0,
        'common_passwords': 0
    }
    
    common_weak = ['password', '123456', 'admin', 'letmein', 'welcome', 'qwerty', 'abc123']
    
    for pwd in passwords:
        pwd_str = str(pwd).lower()
        pwd_len = len(pwd_str)
        
        # Check for weak patterns
        if pwd_len < 8:
            common_patterns['short_length'] += 1
            weak_passwords.append(pwd)
        
        if any(weak in pwd_str for weak in common_weak):
            common_patterns['common_passwords'] += 1
            weak_passwords.append(pwd)
        
        if re.search(r'\b(19|20)\d{2}\b', pwd_str):
            common_patterns['contains_year'] += 1
        
        if re.search(r'(123|abc|password|admin)', pwd_str):
            common_patterns['simple_pattern'] += 1
    
    # Display results
    console.print(f"\n[bold green]Password Analysis Results:[/bold green]")
    console.print(f"   • Total passwords analyzed: {len(passwords)}")
    console.print(f"   • Potentially weak passwords: {len(set(weak_passwords))}")
    console.print(f"   • Short passwords (< 8 chars): {common_patterns['short_length']}")
    console.print(f"   • Common weak passwords: {common_patterns['common_passwords']}")
    console.print(f"   • Contains year patterns: {common_patterns['contains_year']}")
    console.print(f"   • Simple patterns detected: {common_patterns['simple_pattern']}")
    
    # Save analysis to file
    analysis_file = file_name.replace('.csv', '_password_analysis.txt')
    with open(analysis_file, 'w') as f:
        f.write("Password Analysis Report\n")
        f.write("======================\n\n")
        f.write(f"Total passwords analyzed: {len(passwords)}\n")
        f.write(f"Potentially weak passwords: {len(set(weak_passwords))}\n")
        f.write(f"Short passwords (< 8 chars): {common_patterns['short_length']}\n")
        f.write(f"Common weak passwords: {common_patterns['common_passwords']}\n")
        f.write(f"Contains year patterns: {common_patterns['contains_year']}\n")
        f.write(f"Simple patterns detected: {common_patterns['simple_pattern']}\n\n")
        
        if weak_passwords:
            f.write("Potentially Weak Passwords:\n")
            f.write("-" * 30 + "\n")
            for pwd in set(weak_passwords):
                f.write(f"{pwd}\n")
    
    console.print(f"[green]✅ Password analysis saved to {analysis_file}[/green]")

def generate_field_summary_report(df: pd.DataFrame, file_name: str) -> None:
    """
    Generate a detailed field summary report.
    
    Args:
        df: DataFrame to analyze
        file_name: Base file name for saving the report
    """
    console.print("\n[bold cyan]🔍 Generating Field Summary Report[/bold cyan]")
    
    report_file = file_name.replace('.csv', '_field_summary.txt')
    
    with open(report_file, 'w') as f:
        f.write("Detailed Field Summary Report\n")
        f.write("============================\n\n")
        f.write(f"Total Records: {len(df)}\n")
        f.write(f"Total Columns: {len(df.columns)}\n\n")
        
        f.write("Column Details:\n")
        f.write("-" * 50 + "\n")
        
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            null_count = df[col].isna().sum()
            unique_count = df[col].nunique()
            data_type = str(df[col].dtype)
            
            f.write(f"\nColumn: {col}\n")
            f.write(f"  Data Type: {data_type}\n")
            f.write(f"  Non-null values: {non_null_count}\n")
            f.write(f"  Null values: {null_count}\n")
            f.write(f"  Unique values: {unique_count}\n")
            
            # Sample values
            sample_values = df[col].dropna().head(5).tolist()
            if sample_values:
                f.write(f"  Sample values: {', '.join(str(v)[:50] for v in sample_values)}\n")
    
    console.print(f"[green]✅ Field summary report saved to {report_file}[/green]")

def perform_hash_cracking(df: pd.DataFrame, hash_columns: List[str]) -> Optional[pd.DataFrame]:
    """
    Attempt to crack hashes from the DataFrame and return results.
    
    Args:
        df: DataFrame with hash columns
        hash_columns: List of hash columns to attempt cracking
    
    Returns:
        DataFrame with cracked results or None if cracking was not performed
    """
    # Detect available tools
    tools = detect_tools()
    if not any(tools.values()):
        console.print("[red]No cracking tools installed. Exiting.[/red]")
        return None

    # Choose the cracking tool
    tool = choose_tool(tools)

    # Get wordlist and hash type
    wordlist = get_wordlist()
    hash_type = get_hash_type()

    # Prepare a temporary file with hashes
    with tempfile.NamedTemporaryFile(delete=False, mode='w+t') as hash_file:
        for col in hash_columns:
            # Write unique hashes to file
            unique_hashes = df[col].dropna().unique()
            for h in unique_hashes:
                hash_file.write(f"{h}\n")
        hash_file_path = hash_file.name

    # Confirm before cracking
    confirm = Confirm.ask(f"Proceed to crack using {tool} with {wordlist}?", default=True)
    if not confirm:
        console.print("[yellow]Cracking cancelled by user.[/yellow]")
        return None

    start_time = time()
    command = spawn_cracking_tool(tool, hash_file_path, hash_type, wordlist)
    return_code = capture_output(command)
    end_time = time()

    if return_code == 0:
        duration = end_time - start_time
        cracked_data = parse_output(tool, hash_file_path, duration)
        console.print("[green]Cracking completed successfully.[/green]")

        # Clean up temporary file
        os.unlink(hash_file_path)

        return cracked_data
    else:
        console.print("[red]Cracking failed.[/red]")
        return None


def main():
    """
    Main application entry point and control flow.
    
    Orchestrates the complete application workflow:
    1. Displays welcome banner
    2. Validates API key availability
    3. Prompts user for search type and value
    4. Confirms search parameters
    5. Executes API search and processes results
    6. Handles errors and user interruptions gracefully
    
    The function implements comprehensive error handling for:
    - Missing API keys
    - Empty search values
    - User cancellation (Ctrl+C)
    - Unexpected errors
    
    Returns:
        None: Operates with side effects and may call sys.exit()
        
    Raises:
        SystemExit: On critical errors or user cancellation
    
    Example:
        >>> if __name__ == "__main__":
        >>>     main()  # Starts the interactive CLI application
    """
    try:
        # Print welcome banner
        print_welcome_banner()
        
        # Check if API credentials are available
        email, api_key = get_api_credentials()
        if not email or not api_key:
            console.print("[red]❌ Missing API credentials![/red]")
            console.print("\n[yellow]Please set up your API credentials first:[/yellow]")
            console.print("1. Set environment variables: DEHASHED_EMAIL and DEHASHED_API_KEY")
            console.print("2. Or update config.ini with both email and API key")
            console.print("\nSee README.md for detailed instructions.")
            sys.exit(1)
        
        console.print("[green]✅ API credentials loaded successfully[/green]")
        console.print()
        
        # Get search choice
        search_type = get_search_choice()
        
        # Get search value
        search_value = get_search_value(search_type)
        
        if not search_value:
            console.print("[red]❌ No search value provided. Exiting.[/red]")
            sys.exit(1)
        
        # Confirm before API call
        if confirm_search(search_type, search_value):
            # Perform API search and handle results within the function
            success = perform_api_search(search_type, search_value, email, api_key)
            if success:
                console.print("[green]✅ Process completed successfully.[/green]")
            else:
                console.print("[red]❌ Search failed or returned no results.[/red]")
        else:
            console.print("[yellow]Search cancelled by user.[/yellow]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]❌ An error occurred: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()

