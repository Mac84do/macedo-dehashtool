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

# Initialize Rich console
console = Console()

def print_welcome_banner():
    """Print a welcome banner using Rich."""
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
    """Get the user's search choice."""
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
    """Get the domain or email value from user."""
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
    """Confirm the search before calling the API."""
    search_type_name = "Domain" if search_type == "1" else "Email"
    
    console.print()
    console.print(f"[bold]Search Summary:[/bold]")
    console.print(f"Type: {search_type_name} search")
    console.print(f"Value: [cyan]{search_value}[/cyan]")
    console.print()
    
    return Confirm.ask("Proceed with API search?", default=True)

def perform_api_search(search_type, search_value, api_key):
    """Perform the actual API search and extract results."""
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
        else:
            console.print("[bold red]No valid email/password pairs found.[/bold red]")

    except (DeHashedRateLimitError, DeHashedAPIError, DeHashedError) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def main():
    """Main application entry point."""
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
