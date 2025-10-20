"""
CDP Runbook Creator - Version 2.0

A secure, cross-platform tool for automating CDP engagement workflows in Quip.

Features:
- Secure encrypted token storage
- Cross-platform compatibility (Linux, macOS, Windows)
- Automatic migration from insecure storage
- Bulk user management from CSV files
- Professional UI with progress tracking

Usage:
    cdpRunbooker                    # Interactive mode
    cdpRunbooker --add-users file.csv
    cdpRunbooker --download THREAD_ID
    cdpRunbooker --debug
"""

__version__ = "2.0.0"
__author__ = "fieldinn@"
__email__ = "fieldinn@amazon.com"

# Make the main function available for the console script entry point
from cdpRunbooker import main

__all__ = ['main']
