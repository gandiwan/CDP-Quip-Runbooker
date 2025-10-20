"""
Core CDP Runbooker modules for Quip API interactions.
"""

from .secure_token_manager import SecureTokenManager
from .models import DocumentResult, FolderInfo

# Backward compatibility alias
TokenManager = SecureTokenManager

__all__ = [
    'SecureTokenManager',
    'TokenManager',  # Backward compatibility
    'DocumentResult',
    'FolderInfo'
]
