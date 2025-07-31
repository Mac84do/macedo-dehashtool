#!/usr/bin/env python3
"""
Installation script for macedo-dehashtool
Supports installing v1 (basic) or v2 (enhanced) versions
"""

import subprocess
import sys
import argparse

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def install_v1():
    """Install v1 with basic dependencies"""
    print("Installing macedo-dehashtool v1 (basic version)...")
    run_command("pip install requests python-dotenv")
    print("✓ v1 dependencies installed successfully!")
    print("Usage: python main.py [options]")

def install_v2():
    """Install v2 with enhanced dependencies"""
    print("Installing macedo-dehashtool v2 (enhanced version)...")
    run_command("pip install requests python-dotenv numpy pandas rich reportlab typer")
    print("✓ v2 dependencies installed successfully!")
    print("Usage: python main_v2.py [options]")

def install_both():
    """Install both versions"""
    print("Installing both v1 and v2 versions...")
    install_v2()  # v2 includes all v1 dependencies
    print("✓ Both versions installed successfully!")
    print("Usage:")
    print("  v1: python main.py [options]")
    print("  v2: python main_v2.py [options]")

def main():
    parser = argparse.ArgumentParser(description="Install macedo-dehashtool")
    parser.add_argument('--version', choices=['v1', 'v2', 'both'], default='both',
                       help='Version to install (default: both)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Macedo Dehashing Tool Installation")
    print("=" * 50)
    
    if args.version == 'v1':
        install_v1()
    elif args.version == 'v2':
        install_v2()
    else:
        install_both()
    
    print("\nInstallation complete!")
    print("\nNote: For v2 hash cracking features, you may also need to install:")
    print("  - hashcat: https://hashcat.net/hashcat/")
    print("  - john the ripper: https://www.openwall.com/john/")

if __name__ == "__main__":
    main()
