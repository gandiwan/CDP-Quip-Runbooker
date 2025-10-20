"""
CSV processing utilities for CDP Runbooker.
"""

import csv
import re
import os
from typing import List, Dict, Tuple
import logging
import sys

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.user_interface import msg
except ImportError:
    # Fallback for when running as standalone
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from utils.user_interface import msg
    except ImportError:
        # Final fallback - create a simple msg function
        class SimpleMsg:
            @staticmethod
            def print_error(text): print(f"ERROR: {text}")
            @staticmethod
            def print_info(text): print(f"INFO: {text}")
            @staticmethod
            def print_warning(text): print(f"WARNING: {text}")
        msg = SimpleMsg()

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Handles CSV file processing and email extraction."""
    
    @staticmethod
    def extract_emails_from_csv(csv_file_path: str, debug_mode: bool = False) -> List[str]:
        """
        Extract email addresses from a CSV file, supporting multiple formats.
        
        Args:
            csv_file_path (str): Path to the CSV file
            debug_mode (bool): Enable debug logging
            
        Returns:
            list: List of email addresses found in the file
        """
        emails = []
        
        try:
            if not os.path.exists(csv_file_path):
                logger.error(f" CSV file not found: {csv_file_path}")
                return []
            
            # Check for Excel-style sep= directive
            delimiter = ','
            with open(csv_file_path, 'r', encoding='utf-8', errors='ignore') as check_file:
                first_line = check_file.readline().strip()
                if 'sep=' in first_line:
                    delimiter = first_line[first_line.index('sep=') + 4:first_line.index('sep=') + 5]
                    if debug_mode:
                        logger.debug(f" Detected delimiter: '{delimiter}'")
            
            with open(csv_file_path, 'r', encoding='utf-8', errors='ignore') as csv_file:
                # Skip Excel separator directive if present
                if 'sep=' in csv_file.readline():
                    pass  # Line already consumed
                else:
                    csv_file.seek(0)  # Reset if no directive
                
                # Try to detect if it's a simple email list
                first_line = csv_file.readline().strip()
                is_email_list = '@' in first_line and ',' in first_line and \
                               not any(header in first_line.lower() for header in ['email', 'name', 'login', 'user'])
                
                csv_file.seek(0)
                if 'sep=' in csv_file.readline():
                    pass  # Skip directive again
                else:
                    csv_file.seek(0)
                
                if is_email_list:
                    # Handle simple comma-separated email list
                    content = csv_file.read()
                    found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
                    emails = [email.strip() for email in found_emails if email.strip()]
                else:
                    # Handle structured CSV
                    emails = CSVProcessor._extract_from_structured_csv(csv_file, delimiter, debug_mode)
        
        except Exception as e:
            logger.error(f" Error extracting emails from CSV: {str(e)}")
            return []
        
        # Remove duplicates while preserving order
        unique_emails = []
        seen = set()
        for email in emails:
            if email.lower() not in seen:
                unique_emails.append(email)
                seen.add(email.lower())
        
        logger.info(f" Extracted {len(unique_emails)} unique email addresses from CSV")
        return unique_emails
    
    @staticmethod
    def _extract_from_structured_csv(csv_file, delimiter: str, debug_mode: bool) -> List[str]:
        """Extract emails from structured CSV with headers."""
        emails = []
        
        try:
            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
            fieldnames = csv_reader.fieldnames
            
            if not fieldnames:
                return []
            
            # Find email and login columns
            email_col = None
            login_col = None
            
            for field in fieldnames:
                field_lower = field.lower()
                if field_lower in ['email', 'e-mail', 'user email', 'email address'] and not email_col:
                    email_col = field
                elif field_lower in ['login', 'user', 'username', 'alias', 'userid'] and not login_col:
                    login_col = field
            
            # Process rows
            for row in csv_reader:
                email = None
                if email_col and email_col in row and row[email_col]:
                    email = row[email_col].strip()
                elif login_col and login_col in row and row[login_col]:
                    login = row[login_col].strip()
                    email = login if '@' in login else f"{login}@amazon.com"
                
                if email:
                    emails.append(email)
        
        except Exception as e:
            if debug_mode:
                logger.debug(f" Structured CSV extraction error: {str(e)}")
        
        return emails
    
    @staticmethod
    def clean_csv_file(input_file_path: str) -> str:
        """Create a cleaned version of a CSV file."""
        try:
            file_dir = os.path.dirname(input_file_path) or '.'
            file_name = os.path.basename(input_file_path)
            cleaned_file_path = os.path.join(file_dir, f"cleaned_{file_name}")
            
            with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as in_file:
                content = in_file.readlines()
            
            # Remove Excel separator directive if present
            if content and 'sep=' in content[0]:
                content = content[1:]
            
            with open(cleaned_file_path, 'w', encoding='utf-8', newline='') as out_file:
                out_file.writelines(content)
            
            logger.info(f" Created clean CSV file at {cleaned_file_path}")
            return cleaned_file_path
            
        except Exception as e:
            logger.error(f" Failed to clean CSV file: {str(e)}")
            return input_file_path
