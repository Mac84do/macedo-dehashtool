#!/usr/bin/env python3
"""
Lazy imports module for optional dependencies.

This module provides lazy import functionality with informative error messages
for optional dependencies that may not be installed. This allows the core
functionality to work without requiring all optional dependencies.

Usage:
    from lazy_imports import lazy_import_reportlab, lazy_import_pandas, lazy_import_rich
    
    # Use lazy imports with error handling
    reportlab = lazy_import_reportlab()
    if reportlab:
        # Use reportlab functionality
        pass
"""

import sys
from typing import Optional, Any


def lazy_import_reportlab() -> Optional[Any]:
    """
    Lazily import reportlab with informative error handling.
    
    Returns:
        reportlab module if available, None if not installed
        
    Raises:
        ImportError: With helpful installation instructions if reportlab is missing
    """
    try:
        import reportlab
        return reportlab
    except ImportError:
        error_msg = (
            "\n❌ ReportLab is required for PDF generation but is not installed.\n"
            "\n📦 To install ReportLab, run one of the following commands:\n"
            "   pip install reportlab>=4.0.0\n"
            "   pip install -r requirements_v2.txt\n"
            "\n📚 ReportLab is used for:\n"
            "   • Creating PDF reports from CSV data\n"
            "   • Generating formatted tables and layouts\n"
            "   • Professional document generation\n"
            "\n🔗 More info: https://pypi.org/project/reportlab/"
        )
        raise ImportError(error_msg)


def lazy_import_pandas() -> Optional[Any]:
    """
    Lazily import pandas with informative error handling.
    
    Returns:
        pandas module if available, None if not installed
        
    Raises:
        ImportError: With helpful installation instructions if pandas is missing
    """
    try:
        import pandas
        return pandas
    except ImportError:
        error_msg = (
            "\n❌ Pandas is required for data processing but is not installed.\n"
            "\n📦 To install Pandas, run one of the following commands:\n"
            "   pip install pandas>=2.0.0\n"
            "   pip install -r requirements_v2.txt\n"
            "\n📚 Pandas is used for:\n"
            "   • CSV data manipulation and analysis\n"
            "   • DataFrame operations for result processing\n"
            "   • Data filtering and extraction\n"
            "\n🔗 More info: https://pypi.org/project/pandas/"
        )
        raise ImportError(error_msg)


def lazy_import_rich() -> Optional[Any]:
    """
    Lazily import rich with informative error handling.
    
    Returns:
        rich module if available, None if not installed
        
    Raises:
        ImportError: With helpful installation instructions if rich is missing
    """
    try:
        import rich
        return rich
    except ImportError:
        error_msg = (
            "\n❌ Rich is required for enhanced console output but is not installed.\n"
            "\n📦 To install Rich, run one of the following commands:\n"
            "   pip install rich>=13.0.0\n"
            "   pip install -r requirements_v2.txt\n"
            "\n📚 Rich is used for:\n"
            "   • Colorful and formatted console output\n"
            "   • Progress bars and status indicators\n"
            "   • Interactive prompts and confirmations\n"
            "   • Beautiful table and panel displays\n"
            "\n🔗 More info: https://pypi.org/project/rich/"
        )
        raise ImportError(error_msg)


def check_external_tool(tool_name: str) -> bool:
    """
    Check if an external hash cracking tool is available.
    
    Args:
        tool_name: Name of the tool to check ('hashcat' or 'john')
        
    Returns:
        bool: True if tool is available, False otherwise
        
    Raises:
        ImportError: With helpful installation instructions if tool is missing
    """
    import shutil
    
    if shutil.which(tool_name):
        return True
    
    if tool_name.lower() == 'hashcat':
        error_msg = (
            f"\n❌ {tool_name} is required for hash cracking but is not installed.\n"
            "\n📦 To install Hashcat:\n"
            "   • Windows: Download from https://hashcat.net/hashcat/\n"
            "   • Linux: apt install hashcat (Ubuntu/Debian) or yum install hashcat (RHEL/CentOS)\n"
            "   • macOS: brew install hashcat\n"
            "\n📚 Hashcat is used for:\n"
            "   • GPU-accelerated hash cracking\n"
            "   • Multiple hash type support\n"
            "   • Advanced attack modes\n"
            "\n🔗 More info: https://hashcat.net/hashcat/"
        )
    elif tool_name.lower() == 'john':
        error_msg = (
            f"\n❌ {tool_name} is required for hash cracking but is not installed.\n"
            "\n📦 To install John the Ripper:\n"
            "   • Windows: Download from https://www.openwall.com/john/\n"
            "   • Linux: apt install john (Ubuntu/Debian) or yum install john (RHEL/CentOS)\n"
            "   • macOS: brew install john\n"
            "\n📚 John the Ripper is used for:\n"
            "   • CPU-based hash cracking\n"
            "   • Comprehensive hash format support\n"
            "   • Rule-based attacks\n"
            "\n🔗 More info: https://www.openwall.com/john/"
        )
    else:
        error_msg = (
            f"\n❌ {tool_name} is required but is not installed or not in PATH.\n"
            "\n📦 Please install {tool_name} and ensure it's available in your system PATH.\n"
        )
    
    raise ImportError(error_msg)


def safe_import_reportlab():
    """
    Safely import reportlab components, returning None if not available.
    
    Returns:
        dict: Dictionary of reportlab components if available, None if not installed
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        return {
            'colors': colors,
            'pagesizes': {'letter': letter, 'A4': A4, 'landscape': landscape},
            'platypus': {
                'SimpleDocTemplate': SimpleDocTemplate,
                'Table': Table,
                'TableStyle': TableStyle,
                'Paragraph': Paragraph,
                'Spacer': Spacer,
                'PageBreak': PageBreak
            },
            'styles': {'getSampleStyleSheet': getSampleStyleSheet, 'ParagraphStyle': ParagraphStyle},
            'units': {'inch': inch}
        }
    except ImportError:
        return None


def safe_import_pandas():
    """
    Safely import pandas, returning None if not available.
    
    Returns:
        pandas module if available, None if not installed
    """
    try:
        import pandas as pd
        return pd
    except ImportError:
        return None


def safe_import_rich():
    """
    Safely import rich components, returning None if not available.
    
    Returns:
        dict: Dictionary of rich components if available, None if not installed
    """
    try:
        from rich.console import Console
        from rich.live import Live
        from rich.panel import Panel
        from rich.prompt import Prompt, Confirm
        from rich.progress import Progress
        from rich.table import Table
        
        return {
            'Console': Console,
            'Live': Live,
            'Panel': Panel,
            'Prompt': Prompt,
            'Confirm': Confirm,
            'Progress': Progress,
            'Table': Table
        }
    except ImportError:
        return None


# Convenience functions for checking if optional dependencies are available
def has_reportlab() -> bool:
    """Check if reportlab is available."""
    return safe_import_reportlab() is not None


def has_pandas() -> bool:
    """Check if pandas is available."""
    return safe_import_pandas() is not None


def has_rich() -> bool:
    """Check if rich is available."""
    return safe_import_rich() is not None


def has_external_tool(tool_name: str) -> bool:
    """Check if external tool is available without raising errors."""
    import shutil
    return shutil.which(tool_name) is not None


# Module-level checks for easy access
REPORTLAB_AVAILABLE = has_reportlab()
PANDAS_AVAILABLE = has_pandas()
RICH_AVAILABLE = has_rich()
HASHCAT_AVAILABLE = has_external_tool('hashcat')
JOHN_AVAILABLE = has_external_tool('john')
