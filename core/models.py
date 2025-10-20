"""
Data models for CDP Runbooker.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DocumentResult:
    """Result of document creation operations."""
    main_thread_id: str
    documents: Dict[str, str]  # Document name -> URL mapping


@dataclass 
class FolderInfo:
    """Information about a Quip folder."""
    folder_id: str
    folder_name: str
    folder_url: str
    member_count: Optional[int] = None


@dataclass
class UserInfo:
    """Information about a Quip user."""
    user_id: str
    email: str
    name: str


@dataclass
class RateLimitInfo:
    """Rate limiting information from Quip API."""
    remaining: Optional[int] = None
    reset_time: Optional[int] = None
    limit: Optional[int] = None
