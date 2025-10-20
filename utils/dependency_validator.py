#!/usr/bin/env python3
"""
Dependency validation utilities for CDP Runbooker.

This module provides functions to check if all required dependencies are available
and provides helpful guidance when they're missing.
"""

import os
import sys
import subprocess
from typing import List, Tuple, Optional


def get_requirements_list(requirements_file: str = "requirements.txt") -> List[str]:
    """
    Parse requirements.txt and return list of required packages.
    
    Args:
        requirements_file: Path to requirements.txt file
        
    Returns:
        List of package names (without version constraints)
    """
    requirements = []
    
    # Find requirements.txt relative to this script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_path = os.path.join(script_dir, requirements_file)
    
    if not os.path.exists(requirements_path):
        # Fallback requirements if file not found
        return ['quipclient', 'requests', 'urllib3', 'cryptography', 'certifi']
    
    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version constraints)
                    package = line.split('>=')[0].split('==')[0].split('~=')[0].split('>')[0].split('<')[0].strip()
                    if package:
                        requirements.append(package)
    except Exception:
        # Fallback requirements if parsing fails
        return ['quipclient', 'requests', 'urllib3', 'cryptography', 'certifi']
    
    return requirements


def check_dependency(package_name: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a specific dependency is available.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        Tuple of (is_available, error_message)
    """
    try:
        __import__(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error importing {package_name}: {str(e)}"


def validate_all_dependencies() -> Tuple[bool, List[str], List[str]]:
    """
    Validate all required dependencies.
    
    Returns:
        Tuple of (all_satisfied, missing_packages, error_messages)
    """
    requirements = get_requirements_list()
    missing_packages = []
    error_messages = []
    
    for package in requirements:
        available, error = check_dependency(package)
        if not available:
            missing_packages.append(package)
            if error:
                error_messages.append(f"  ❌ {package}: {error}")
    
    return len(missing_packages) == 0, missing_packages, error_messages


def get_install_path() -> str:
    """
    Get the recommended installation path for the user.
    
    Returns:
        String with installation command path
    """
    # Try to find the package root directory
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if we're in a git repository
    if os.path.exists(os.path.join(script_dir, '.git')):
        return script_dir
    
    # Check if setup.py exists
    if os.path.exists(os.path.join(script_dir, 'setup.py')):
        return script_dir
    
    # Fallback
    return os.getcwd()


def print_dependency_error(missing_packages: List[str], error_messages: List[str]) -> None:
    """
    Print a helpful dependency error message.
    
    Args:
        missing_packages: List of missing package names
        error_messages: List of formatted error messages
    """
    print("\n" + "="*80)
    print("🔴 DEPENDENCY ERROR - Missing Required Packages")
    print("="*80)
    print()
    print("It looks like you pulled updates that added new dependencies,")
    print("but haven't reinstalled the package to get the new requirements.")
    print()
    print("📦 Missing Dependencies:")
    for msg in error_messages:
        print(msg)
    print()
    print("💡 QUICK FIX:")
    install_path = get_install_path()
    print(f"cd {install_path}")
    print("pip install -e .")
    print()
    print("🔄 This will install/update all required packages and fix the issue.")
    print()
    print("📚 For more help, see the troubleshooting section in README.md")
    print("="*80)


def validate_dependencies_with_helpful_exit() -> None:
    """
    Validate dependencies and exit with helpful message if any are missing.
    This is the main function that should be called at script startup.
    """
    all_satisfied, missing_packages, error_messages = validate_all_dependencies()
    
    if not all_satisfied:
        print_dependency_error(missing_packages, error_messages)
        print("\n💀 Exiting until dependencies are resolved...")
        sys.exit(1)


def check_installation_currency() -> None:
    """
    Check if the current installation might be out of date.
    Provides a warning but doesn't exit.
    """
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_path = os.path.join(script_dir, 'requirements.txt')
        
        if not os.path.exists(requirements_path):
            return  # Can't check without requirements file
        
        # Get modification time of requirements.txt
        import stat
        req_mtime = os.stat(requirements_path)[stat.ST_MTIME]
        
        # Try to find when the package was installed by checking __pycache__
        pycache_dir = os.path.join(script_dir, '__pycache__')
        if os.path.exists(pycache_dir):
            # Get the newest file in __pycache__
            newest_cache = 0
            for filename in os.listdir(pycache_dir):
                filepath = os.path.join(pycache_dir, filename)
                if os.path.isfile(filepath):
                    file_mtime = os.stat(filepath)[stat.ST_MTIME]
                    newest_cache = max(newest_cache, file_mtime)
            
            # If requirements.txt is newer than the cache, warn user
            if req_mtime > newest_cache:
                print("⚠️  Dependencies may have changed since last install")
                print("   Consider running: pip install -e . to update")
                print()
    
    except Exception:
        # Don't block execution if we can't check
        pass


if __name__ == "__main__":
    # Allow testing this module directly
    print("Testing dependency validation...")
    validate_dependencies_with_helpful_exit()
    print("✅ All dependencies satisfied!")
