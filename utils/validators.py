"""
Input validation utilities for CDP Runbooker.
"""

import re
from datetime import datetime
from typing import Optional


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate date format (YYYY-MM)."""
        try:
            datetime.strptime(date_str, '%Y-%m')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_folder_name(name: str) -> bool:
        """Validate folder name doesn't contain invalid characters."""
        return not re.search(r'[<>:"/\\|?*]', name)
    
    @staticmethod
    def validate_sim_id(sim_id: str) -> Optional[str]:
        """Validate and format SIM ID."""
        if not sim_id:
            return ""
            
        # Case 1: Just the number
        if sim_id.isdigit():
            return f"Countdown-Premium-{sim_id}"
        
        # Case 2: Full URL
        if "issues.amazon.com" in sim_id:
            match = re.search(r'(Countdown-Premium-\d+)', sim_id)
            if match:
                return match.group(1)
        
        # Case 3: Already proper format
        if sim_id.startswith("Countdown-Premium-"):
            return sim_id
        
        # Invalid format
        return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
