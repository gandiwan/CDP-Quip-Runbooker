"""
Secure, cross-platform token management for CDP Runbooker.

This module provides encrypted token storage that works consistently across
Linux, macOS, and Windows without relying on shell configuration files.
"""

import os
import sys
import json
import platform
import hashlib
import getpass
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from pathlib import Path

# Set up debug mode
DEBUG_MODE = os.environ.get("CDP_DEBUG", "").lower() in ["true", "1", "yes"]
logger = logging.getLogger(__name__)

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available - tokens will be stored in base64 encoding only")

# Robust import handling for user_interface
msg = None

try:
    # Try absolute import first (when run directly)
    from utils.user_interface import msg
except ImportError:
    try:
        # Try with path manipulation
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from utils.user_interface import msg
    except ImportError:
        # Create a minimal fallback msg object
        class MinimalMsg:
            @staticmethod
            def print_error(message): print(f"ERROR: {message}")
            @staticmethod
            def print_warning(message): print(f"WARNING: {message}")
            @staticmethod
            def print_info(message): print(f"INFO: {message}")
            @staticmethod
            def print_success(message): print(f"SUCCESS: {message}")
            @staticmethod
            def print_header(message): print(f"\n=== {message} ===")
            @staticmethod
            def get_user_input(prompt, required=True):
                while True:
                    value = input(f"{prompt}: ").strip()
                    if value or not required:
                        return value
                    print("This field is required. Please enter a value.")
            @staticmethod
            def get_user_choice(prompt, choices, default=None):
                choices_str = "/".join(choices)
                if default:
                    full_prompt = f"{prompt} ({choices_str}) [{default}]"
                else:
                    full_prompt = f"{prompt} ({choices_str})"
                while True:
                    response = input(f"{full_prompt}: ").lower().strip()
                    if not response and default:
                        return default.lower()
                    if response in [choice.lower() for choice in choices]:
                        return response
                    print(f"Please enter one of: {choices_str}")
        
        msg = MinimalMsg()


class SecureTokenManager:
    """
    Unified secure, cross-platform Quip API token storage and management.
    
    This class handles:
    - Secure encrypted token storage across platforms
    - Automatic migration from legacy shell config storage
    - Token validation and renewal workflow
    - Cross-platform compatibility (Linux, macOS, Windows)
    """
    
    CONFIG_VERSION = "1.0"
    CONFIG_FILENAME = "config.json"
    
    def __init__(self):
        """Initialize the secure token manager."""
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self._ensure_config_directory()
        
        # Global flag to track if token was saved to config file during this session
        self._token_saved_to_config = False
    
    def get_secure_token(self) -> str:
        """
        Get a validated API token using secure storage with automatic migration.
        
        This method provides the main entry point for token management:
        1. Check for existing secure token
        2. Validate token and return if valid
        3. Check for legacy tokens and migrate if found
        4. Guide user through new token setup if needed
        
        Returns:
            str: A valid API token
            
        Raises:
            ValueError: If token cannot be obtained or validated
        """
        # First check if we already have a secure token
        token = self._load_secure_token()
        if token:
            # Validate the token
            user_info = self._validate_token(token)
            if user_info:
                if DEBUG_MODE:
                    logger.debug(f"Loaded valid token from secure storage for user: {user_info.get('name', 'Unknown')}")
                return token
            else:
                if DEBUG_MODE:
                    logger.debug("Secure token validation failed - token may be expired")
                # Token is invalid, remove it and continue with setup
                self._remove_secure_token()
        
        # Check for legacy tokens and migrate if found
        legacy_tokens = self._detect_legacy_tokens()
        if legacy_tokens:
            migrated_token = self._handle_migration(legacy_tokens)
            if migrated_token:
                return migrated_token
        
        # No valid token found, guide user through setup
        return self._setup_new_token()
    
    def store_token_securely(self, token: str) -> bool:
        """
        Store a token securely with encryption.
        
        Args:
            token: The API token to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate token before storing
            user_info = self._validate_token(token)
            if not user_info:
                logger.error("Cannot store invalid token")
                return False
            
            # Encrypt and store the token
            encrypted_token = self._encrypt_token(token)
            
            config_data = {
                "version": self.CONFIG_VERSION,
                "encrypted_token": encrypted_token,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_used": datetime.now(timezone.utc).isoformat(),
                "user_name": user_info.get('name', 'Unknown')
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            # Set secure file permissions
            self._set_secure_permissions(self.config_file)
            
            if DEBUG_MODE:
                logger.debug(f"Token stored securely in {self.config_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store token securely: {str(e)}")
            return False
    
    def _get_config_directory(self) -> Path:
        """Get the platform-appropriate configuration directory."""
        system = platform.system().lower()
        
        if system == 'windows':
            # Windows: %APPDATA%\cdp-runbooker
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata) / 'cdp-runbooker'
            else:
                return Path.home() / 'AppData' / 'Roaming' / 'cdp-runbooker'
        else:
            # Linux/macOS: ~/.config/cdp-runbooker
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                return Path(xdg_config) / 'cdp-runbooker'
            else:
                return Path.home() / '.config' / 'cdp-runbooker'
    
    def _ensure_config_directory(self):
        """Ensure the configuration directory exists with proper permissions."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Set directory permissions (Unix-like systems only)
            if platform.system() != 'Windows':
                os.chmod(self.config_dir, 0o700)  # rwx------
                
        except Exception as e:
            logger.error(f"Failed to create config directory {self.config_dir}: {str(e)}")
            raise
    
    def _set_secure_permissions(self, file_path: Path):
        """Set secure file permissions."""
        try:
            if platform.system() == 'Windows':
                # Windows: Use basic file attributes (hidden + system)
                import stat
                os.chmod(file_path, stat.S_IREAD | stat.S_IWRITE)
            else:
                # Unix-like: Set to 600 (rw-------)
                os.chmod(file_path, 0o600)
        except Exception as e:
            logger.warning(f"Failed to set secure permissions on {file_path}: {str(e)}")
    
    def _generate_encryption_key(self) -> bytes:
        """Generate a deterministic encryption key based on machine/user characteristics."""
        # Create a machine/user-specific salt
        machine_id = platform.node() or "unknown-machine"
        user_id = getpass.getuser() or "unknown-user"
        home_path = str(Path.home())
        
        # Combine identifiers
        identifier = f"{machine_id}:{user_id}:{home_path}:cdp-runbooker-v1"
        
        if DEBUG_MODE:
            logger.debug(f"Generating key from identifier: {machine_id}:{user_id}:***:cdp-runbooker-v1")
        
        # Generate a deterministic key
        salt = hashlib.sha256(identifier.encode()).digest()[:16]
        
        if CRYPTO_AVAILABLE:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(identifier.encode()))
            return key
        else:
            # Fallback to simple base64 encoding
            return base64.urlsafe_b64encode(hashlib.sha256(identifier.encode()).digest())
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt a token for secure storage."""
        if CRYPTO_AVAILABLE:
            key = self._generate_encryption_key()
            f = Fernet(key)
            encrypted = f.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        else:
            # Fallback to base64 encoding (not secure, but better than plaintext)
            logger.warning("Using base64 encoding instead of encryption - install cryptography library for better security")
            return base64.urlsafe_b64encode(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> Optional[str]:
        """Decrypt a token from secure storage."""
        try:
            if CRYPTO_AVAILABLE:
                key = self._generate_encryption_key()
                f = Fernet(key)
                encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
                decrypted = f.decrypt(encrypted_bytes)
                return decrypted.decode()
            else:
                # Fallback base64 decoding
                return base64.urlsafe_b64decode(encrypted_token.encode()).decode()
        except Exception as e:
            if DEBUG_MODE:
                logger.debug(f"Failed to decrypt token: {str(e)}")
            return None
    
    def _load_secure_token(self) -> Optional[str]:
        """Load token from secure storage."""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if config_data.get('version') != self.CONFIG_VERSION:
                if DEBUG_MODE:
                    logger.debug(f"Config version mismatch: {config_data.get('version')} != {self.CONFIG_VERSION}")
                return None
            
            encrypted_token = config_data.get('encrypted_token')
            if not encrypted_token:
                return None
            
            token = self._decrypt_token(encrypted_token)
            if token:
                # Update last used timestamp
                config_data['last_used'] = datetime.now(timezone.utc).isoformat()
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2)
            
            return token
            
        except Exception as e:
            if DEBUG_MODE:
                logger.debug(f"Failed to load secure token: {str(e)}")
            return None
    
    def _remove_secure_token(self):
        """Remove the secure token file."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                if DEBUG_MODE:
                    logger.debug("Removed invalid secure token file")
        except Exception as e:
            logger.warning(f"Failed to remove secure token file: {str(e)}")
    
    def _detect_legacy_tokens(self) -> List[Tuple[str, str]]:
        """
        Detect legacy tokens stored in shell configuration files.
        
        Returns:
            List of (config_file_path, token) tuples
        """
        legacy_tokens = []
        config_files = self._get_shell_config_files()
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Look for CDP Runbooker added tokens
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line == "# Added by CDP Runbooker":
                        # Check the next line for the token
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line.startswith('export QUIP_API_TOKEN='):
                                token = self._extract_token_from_line(next_line)
                                if token:
                                    legacy_tokens.append((config_file, token))
                                    break  # Only find first occurrence per file
                
            except Exception as e:
                if DEBUG_MODE:
                    logger.debug(f"Error reading config file {config_file}: {str(e)}")
                continue
        
        return legacy_tokens
    
    def _get_shell_config_files(self) -> List[str]:
        """Get list of shell configuration files to check."""
        shell = os.environ.get("SHELL", "")
        home = str(Path.home())
        
        config_files = []
        
        if "zsh" in shell:
            config_files.extend([
                os.path.join(home, ".zshrc"),
                os.path.join(home, ".zprofile")
            ])
        elif "bash" in shell:
            config_files.extend([
                os.path.join(home, ".bashrc"),
                os.path.join(home, ".bash_profile")
            ])
        else:
            # Check all common config files
            config_files.extend([
                os.path.join(home, ".zshrc"),
                os.path.join(home, ".bashrc"),
                os.path.join(home, ".bash_profile"),
                os.path.join(home, ".zprofile")
            ])
        
        return config_files
    
    def _extract_token_from_line(self, line: str) -> Optional[str]:
        """Extract token from an export line."""
        try:
            if '=' not in line:
                return None
                
            _, token_part = line.split('=', 1)
            token_part = token_part.strip()
            
            # Handle different quote styles
            if token_part.startswith('"') and token_part.endswith('"'):
                token = token_part[1:-1]
            elif token_part.startswith("'") and token_part.endswith("'"):
                token = token_part[1:-1]
            else:
                token = token_part
            
            # Basic validation
            if token and len(token) > 30:
                return token
                
        except Exception:
            pass
        
        return None
    
    def _handle_migration(self, legacy_tokens: List[Tuple[str, str]]) -> Optional[str]:
        """
        Handle migration from legacy shell config storage.
        
        Args:
            legacy_tokens: List of (config_file, token) tuples
            
        Returns:
            str: Migrated token if successful, None otherwise
        """
        try:
            msg.print_header("Security Notice: Insecure Token Storage Detected!")
            msg.print_warning("We found API tokens stored insecurely in your shell configuration:")
            
            for config_file, _ in legacy_tokens:
                print(f"  • {config_file} (added by CDP Runbooker)")
            
            print("\nFor better security, we'll migrate to encrypted storage and remove")
            print("the insecure entries.")
            print("\nThis will:")
            print("✓ Move your token to encrypted, cross-platform storage")
            print("✓ Remove plaintext tokens from shell configs")
            print("✓ Keep your token working in all environments")
            
            choice = msg.get_user_choice("\nContinue with migration?", ["y", "n"], "y")
            
            if choice not in ['y', 'yes']:
                msg.print_info("Migration cancelled. You can run the script again to migrate later.")
                return None
            
            # Use the first valid token found
            selected_token = None
            for _, token in legacy_tokens:
                user_info = self._validate_token(token)
                if user_info:
                    selected_token = token
                    break
            
            if not selected_token:
                msg.print_error("No valid tokens found in legacy storage. Please set up a new token.")
                return self._setup_new_token()
            
            # Store token securely
            if self.store_token_securely(selected_token):
                # Clean up legacy tokens
                cleaned_files = self._cleanup_legacy_tokens(legacy_tokens)
                
                msg.print_success("Migration Complete!")
                print("✓ Token encrypted and stored securely")
                if cleaned_files:
                    print(f"✓ Removed insecure entries from: {', '.join(cleaned_files)}")
                print("✓ Your token is now protected and cross-platform compatible")
                print("\nYour CDP Runbooker is ready to use!")
                
                return selected_token
            else:
                msg.print_error("Failed to store token securely. Please try manual setup.")
                return self._setup_new_token()
                
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            msg.print_error("Migration failed. Please set up a new token.")
            return self._setup_new_token()
    
    def _cleanup_legacy_tokens(self, legacy_tokens: List[Tuple[str, str]]) -> List[str]:
        """
        Remove legacy tokens from shell configuration files.
        
        Args:
            legacy_tokens: List of (config_file, token) tuples
            
        Returns:
            List of cleaned config file names
        """
        cleaned_files = []
        
        for config_file, _ in legacy_tokens:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Remove CDP Runbooker token entries
                new_lines = []
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line == "# Added by CDP Runbooker":
                        # Skip this line and the next line (token export)
                        i += 1
                        if i < len(lines) and lines[i].strip().startswith('export QUIP_API_TOKEN='):
                            i += 1  # Skip the token line too
                        continue
                    else:
                        new_lines.append(lines[i])
                        i += 1
                
                # Write back to file
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                cleaned_files.append(os.path.basename(config_file))
                
            except Exception as e:
                logger.warning(f"Failed to clean up {config_file}: {str(e)}")
                continue
        
        return cleaned_files
    
    def _setup_new_token(self) -> str:
        """
        Guide user through setting up a new token.
        
        Returns:
            str: The new valid token
            
        Raises:
            ValueError: If token setup fails
        """
        import webbrowser
        
        msg.print_header("Quip API Token Setup")
        msg.print_info("To use this program, you need a Quip API token.")
        
        choice = msg.get_user_choice("Would you like help getting your token now?", ["y", "n"], "y")
        
        if choice not in ['y', 'yes']:
            raise ValueError("Token setup cancelled. Please set up your token to continue.")
        
        msg.print_info("Opening the Quip API token page in your web browser...")
        token_url = "https://quip-amazon.com/dev/token"
        
        browser_opened = False
        try:
            browser_opened = webbrowser.open(token_url)
        except Exception as e:
            msg.print_warning(f"Browser open failed with exception: {e}")
        
        if not browser_opened:
            msg.print_warning("Could not open browser automatically. Please manually visit:")
            print(f"  {token_url}")
        else:
            # Add debug info to understand what's happening
            import os
            display = os.environ.get('DISPLAY', 'Not set')
            msg.print_info(f"Browser command sent (DISPLAY={display})")
        
        print("\nInstructions:")
        print("1. Log in to Quip if prompted")
        print("2. On the token page, copy your Personal Access Token")
        
        while True:
            new_token = msg.get_user_input("Enter your Quip API token")
            
            if not new_token or len(new_token) < 30:
                msg.print_error("The token appears to be invalid (too short). Please try again.")
                continue
            
            # Validate the token
            user_info = self._validate_token(new_token)
            if not user_info:
                msg.print_error("The token is invalid or expired. Please try again.")
                continue
            
            # Token is valid, store it securely
            if self.store_token_securely(new_token):
                msg.print_success("Token setup complete!")
                msg.print_info(f"Authenticated as: {user_info.get('name', 'Unknown')}")
                return new_token
            else:
                msg.print_error("Failed to store token securely. Please try again.")
                continue
    
    def _validate_token(self, token: str, max_retries: int = 3, diagnose_mode: bool = False) -> Optional[dict]:
        """
        Validate token by testing it with the Quip API.
        
        Args:
            token: The API token to validate
            max_retries: Maximum number of retry attempts for network issues
            diagnose_mode: Enable enhanced diagnostic logging
            
        Returns:
            dict: User info if token is valid, None otherwise
        """
        import time
        import ssl
        import urllib3
        import requests
        
        if not token or len(token) < 30:
            if DEBUG_MODE or diagnose_mode:
                logger.debug("Token validation failed: Token is empty or too short")
            return None
        
        # Log Python and SSL information in diagnose mode
        if diagnose_mode:
            import platform
            msg.print_info(f"Python Version: {platform.python_version()}")
            msg.print_info(f"SSL Version: {ssl.OPENSSL_VERSION}")
            msg.print_info(f"Requests Version: {requests.__version__}")
            msg.print_info(f"urllib3 Version: {urllib3.__version__}")
            
            # Log certificate paths
            try:
                import certifi
                msg.print_info(f"Certifi CA Bundle: {certifi.where()}")
            except:
                pass
        
        for attempt in range(max_retries):
            try:
                if DEBUG_MODE or diagnose_mode:
                    logger.debug(f"Token validation attempt {attempt + 1}/{max_retries}")
                    if diagnose_mode:
                        msg.print_info(f"Attempt {attempt + 1}/{max_retries}: Validating token...")
                
                # Import here to avoid circular imports
                try:
                    import amazoncerts
                    if diagnose_mode:
                        msg.print_info("Using amazoncerts module for SSL")
                    import quip
                except ImportError:
                    if diagnose_mode:
                        msg.print_info("amazoncerts not available, using quipclient")
                    import quipclient as quip
                
                # Log API endpoint
                base_url = "https://platform.quip-amazon.com"
                if diagnose_mode:
                    msg.print_info(f"API Base URL: {base_url}")
                    msg.print_info(f"Token Format: {token[:20]}...{token[-10:]} (length: {len(token)})")
                
                # Create a temporary client to test the token
                temp_client = quip.QuipClient(
                    access_token=token,
                    base_url=base_url
                )
                
                # In diagnose mode, try to get more details about the request
                if diagnose_mode:
                    msg.print_info("Making API request to validate token...")
                    
                    # Try to access the underlying session if available
                    if hasattr(temp_client, 'request'):
                        # Make a direct request to see full details
                        try:
                            import json
                            headers = {"Authorization": f"Bearer {token}"}
                            url = f"{base_url}/1/users/current"
                            msg.print_info(f"Direct API URL: {url}")
                            msg.print_info("Request Headers: Authorization: Bearer [REDACTED]")
                            
                            # Make direct request with detailed error handling
                            response = requests.get(url, headers=headers, timeout=30)
                            msg.print_info(f"Response Status: {response.status_code}")
                            msg.print_info(f"Response Headers: {dict(response.headers)}")
                            
                            if response.status_code != 200:
                                msg.print_error(f"API Error Response: {response.text[:500]}")
                            else:
                                user_info = response.json()
                                if user_info and 'id' in user_info:
                                    msg.print_success(f"Direct API validation successful: {user_info.get('name', 'Unknown')}")
                                    return user_info
                        except Exception as direct_e:
                            msg.print_error(f"Direct API request failed: {str(direct_e)}")
                            if hasattr(direct_e, '__class__'):
                                msg.print_error(f"Exception Type: {direct_e.__class__.__name__}")
                
                # Test the token by getting authenticated user
                user_info = temp_client.get_authenticated_user()
                
                if user_info and 'id' in user_info:
                    if DEBUG_MODE or diagnose_mode:
                        logger.debug(f"Token validation successful for user: {user_info.get('name', 'Unknown')}")
                        if diagnose_mode:
                            msg.print_success(f"Token validated successfully: {user_info.get('name', 'Unknown')}")
                    return user_info
                else:
                    if DEBUG_MODE or diagnose_mode:
                        logger.debug("Token validation failed: No user info returned or missing 'id' field")
                        if diagnose_mode:
                            msg.print_error("Token validation failed: Invalid response from API")
                            msg.print_error(f"Response data: {user_info}")
                    return None
                    
            except Exception as e:
                error_str = str(e).lower()
                error_type = type(e).__name__
                
                if DEBUG_MODE or diagnose_mode:
                    logger.debug(f"Token validation attempt {attempt + 1} failed: {str(e)}")
                    if diagnose_mode:
                        msg.print_error(f"Validation Error: {error_type}: {str(e)}")
                        
                        # Log additional details for SSL errors
                        if 'ssl' in error_str or 'certificate' in error_str:
                            msg.print_error("SSL/Certificate error detected")
                            try:
                                import traceback
                                msg.print_error(f"Full traceback:\n{traceback.format_exc()}")
                            except:
                                pass
                
                # Check if it's a network/temporary issue that we should retry
                if any(keyword in error_str for keyword in ['timeout', 'connection', 'network', 'temporary', 'service unavailable', '502', '503', '504']):
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                        if DEBUG_MODE or diagnose_mode:
                            logger.debug(f"Network error detected, retrying in {wait_time}s...")
                            if diagnose_mode:
                                msg.print_info(f"Network error - retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        if DEBUG_MODE or diagnose_mode:
                            logger.debug("Max retries reached for network errors")
                            if diagnose_mode:
                                msg.print_error("Max retries reached for network errors")
                        return None
                
                # Check if it's an authentication error (expired/invalid token)
                elif any(keyword in error_str for keyword in ['unauthorized', '401', 'forbidden', '403', 'invalid', 'expired']):
                    if DEBUG_MODE or diagnose_mode:
                        logger.debug("Authentication error detected - token is likely expired or invalid")
                        if diagnose_mode:
                            msg.print_error("Authentication error - token appears to be invalid or expired")
                    return None
                
                # For other errors, don't retry but log the specific error
                else:
                    if DEBUG_MODE or diagnose_mode:
                        logger.debug(f"Unexpected validation error: {str(e)}")
                        if diagnose_mode:
                            msg.print_error(f"Unexpected error type: {error_type}")
                    return None
        
        # If we get here, all retries failed
        if DEBUG_MODE or diagnose_mode:
            logger.debug("Token validation failed after all retry attempts")
            if diagnose_mode:
                msg.print_error("Token validation failed after all retry attempts")
        return None
    
    # Backward compatibility methods from legacy TokenManager
    def get_api_token(self) -> str:
        """
        Retrieve and validate Quip API token (legacy method for backward compatibility).
        
        Returns:
            str: A valid API token
            
        Raises:
            ValueError: If token cannot be obtained or validated
        """
        return self.get_secure_token()
    
    def get_validated_token(self) -> Tuple[str, dict]:
        """
        Get and validate API token, returning both token and user info.
        
        Returns:
            Tuple[str, dict]: (token, user_info) if valid
            
        Raises:
            ValueError: If token cannot be obtained or validated
        """
        token = self.get_secure_token()
        user_info = self._validate_token(token)
        
        if not user_info:
            raise ValueError("Token validation failed")
            
        return token, user_info
    
    def get_validated_token_with_status(self) -> Tuple[str, dict, bool]:
        """
        Get and validate API token, returning token, user info, and config save status.
        
        Returns:
            Tuple[str, dict, bool]: (token, user_info, config_saved) if valid
            
        Raises:
            ValueError: If token cannot be obtained or validated
        """
        token = self.get_secure_token()
        user_info = self._validate_token(token)
        
        if not user_info:
            raise ValueError("Token validation failed")
            
        return token, user_info, self._token_saved_to_config
    
    def ensure_token_in_environment(self) -> bool:
        """
        Ensure QUIP_API_TOKEN is available in the current environment.
        For backward compatibility - now uses secure storage.
        
        Returns:
            bool: True if token is available, False otherwise
        """
        try:
            token = self.get_secure_token()
            os.environ["QUIP_API_TOKEN"] = token
            return True
        except ValueError:
            return False
    
    def set_token_config_flag(self):
        """Set the global flag indicating token was saved to config."""
        self._token_saved_to_config = True
    
    def diagnose_token(self, token: Optional[str] = None) -> bool:
        """
        Run comprehensive token diagnostics.
        
        Args:
            token: Optional token to test. If not provided, will use stored token.
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        import socket
        
        msg.print_header("CDP Runbooker Token Diagnostics")
        
        # Test 1: Network connectivity
        msg.print_info("Test 1: Network connectivity to quip-amazon.com")
        try:
            socket.gethostbyname('platform.quip-amazon.com')
            msg.print_success("✓ DNS resolution successful")
        except Exception as e:
            msg.print_error(f"✗ DNS resolution failed: {str(e)}")
            return False
        
        # Test 2: HTTPS connectivity
        msg.print_info("\nTest 2: HTTPS connectivity")
        try:
            import requests
            response = requests.get("https://platform.quip-amazon.com", timeout=10)
            msg.print_success(f"✓ HTTPS connection successful (status: {response.status_code})")
        except Exception as e:
            msg.print_error(f"✗ HTTPS connection failed: {type(e).__name__}: {str(e)}")
            return False
        
        # Test 3: Token format
        msg.print_info("\nTest 3: Token format check")
        test_token = token
        if not test_token:
            # Try to load stored token
            test_token = self._load_secure_token()
            if not test_token:
                msg.print_error("✗ No token provided and no stored token found")
                return False
        
        # Check token format
        if len(test_token) < 30:
            msg.print_error(f"✗ Token too short (length: {len(test_token)})")
            return False
        
        # Check for common format patterns
        if '|' in test_token:
            parts = test_token.split('|')
            if len(parts) == 3:
                msg.print_success(f"✓ Token format appears valid (3 parts, total length: {len(test_token)})")
            else:
                msg.print_warning(f"⚠ Unusual token format ({len(parts)} parts)")
        else:
            msg.print_warning("⚠ Token doesn't match expected format (no pipe separators)")
        
        # Test 4: Token validation with detailed diagnostics
        msg.print_info("\nTest 4: Token validation with API")
        result = self._validate_token(test_token, max_retries=1, diagnose_mode=True)
        
        if result:
            msg.print_success(f"\n✓ Token is VALID for user: {result.get('name', 'Unknown')}")
            return True
        else:
            msg.print_error("\n✗ Token validation FAILED")
            msg.print_info("\nPossible causes:")
            msg.print_info("1. Token has expired - get a new one from https://quip-amazon.com/dev/token")
            msg.print_info("2. Token was copied incorrectly - ensure no extra spaces or characters")
            msg.print_info("3. Network/firewall issues - check VPN connection if working remotely")
            msg.print_info("4. SSL/certificate issues - may need to update certificates")
            return False
