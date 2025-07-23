#!/usr/bin/env python3
"""
Main CLI application for Dehashed API tool.

Provides an interactive interface for domain and email searches.
"""

import sys
import os
import re
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from get_api_key import get_api_key
from dehashed import search, DeHashedError, DeHashedRateLimitError, DeHashedAPIError
from result_extraction import extract_email_password_data, print_extraction_summary, print_dataframe_table
from pdf_generator import generate_pdf_report

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
    title = Text("Dehashed API Tool", style="bold cyan")
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

def perform_api_search(search_type, search_value, api_key):
    """
    Execute the DeHashed API search and process results.
    
    Sends a search query to the DeHashed API using provided search type
    and value along with user's API key. Handles response extraction,
    data cleaning, and output generation including CSV and PDF files.
    
    Args:
        search_type (str): The search type ("1" for domain, "2" for email)
        search_value (str): The search query string entered by user
        api_key (str): User's API key for authentication
        
    Returns:
        None: Operates with side effects like creating files and
              printing to the console
    
    Raises:
        DeHashedRateLimitError: When rate limit is hit
        DeHashedAPIError: For unexpected API errors
        DeHashedError: For general errors affecting search
        
    Example:
        [90m>>> perform_api_search("1", "example.com", "your_api_key")
        # Outputs
        ✅ Dataframe saved to output/2025-01-23_example.com.csv
        ✅ PDF report saved to output/2025-01-23_example.com.pdf
    """
    search_type_name = "domain" if search_type == "1" else "email"

    console.print(f"[yellow]Searching Dehashed API for {search_type_name}: {search_value}...[/yellow]")

    try:
        # Perform the search
        response = search(query=search_value, api_key=api_key)
        
        # Extract results
        original_count = len(response.get('entries', []))
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
            os.makedirs(output_dir, exist_ok=True)
            
            # Create file name
            # Sanitize query for filename (replace spaces and special characters)
            query = re.sub(r'[^a-zA-Z0-9._-]', '_', search_value)
            file_name = f"{output_dir}/{date_str}_{query}.csv"
            
            # Save to CSV
            df.to_csv(file_name, index=False)
            console.print(f"[green]✅ Dataframe saved to {file_name}[/green]")
            
            # Generate PDF report
            try:
                pdf_path = generate_pdf_report(file_name)
                console.print(f"[green]✅ PDF report saved to {pdf_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  PDF generation failed: {str(e)}[/yellow]")
        else:
            console.print("[bold red]No valid email/password pairs found.[/bold red]")

    except (DeHashedRateLimitError, DeHashedAPIError, DeHashedError) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

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
        
        # Check if API key is available
        api_key = get_api_key()
        if not api_key:
            console.print("[red]❌ No API key found![/red]")
            console.print("\n[yellow]Please set up your API key first:[/yellow]")
            console.print("1. Set environment variable: DEHASHED_API_KEY=your_key")
            console.print("2. Or create config.ini from config.ini.example")
            console.print("\nSee README_API_KEY.md for detailed instructions.")
            sys.exit(1)
        
        console.print("[green]✅ API key loaded successfully[/green]")
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
            perform_api_search(search_type, search_value, api_key)
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
