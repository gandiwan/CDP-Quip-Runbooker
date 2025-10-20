#!/usr/bin/env python3
"""
CDP Engagement Folder and Runbook Creator (Refactored)

This is a refactored version of the original script that:
- Uses modular components from core/ and utils/
- Removes code duplication 
- Separates concerns properly
- Has better error handling and configuration
- Is more maintainable and readable
"""

def setup_ssl_certificates():
    """Set up SSL certificate path automatically using certifi."""
    import os
    
    # Allow user override via environment variable
    if os.environ.get('SSL_CERT_FILE'):
        print(f"Using existing SSL_CERT_FILE: {os.environ['SSL_CERT_FILE']}")
        return True
    
    try:
        import certifi
        # Set SSL_CERT_FILE environment variable to use certifi's certificate bundle
        cert_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_path
        print(f"SSL certificate path set to: {cert_path}")
        return True
    except ImportError:
        print("Warning: certifi module not found. SSL certificate path not automatically configured.")
        print("You may need to manually set SSL_CERT_FILE environment variable.")
        return False
    except Exception as e:
        print(f"Warning: Could not set SSL certificate path: {e}")
        return False

import os
import sys
import argparse
import logging
import re
import time
import traceback
import atexit
import signal
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s UTC %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set up debug mode
DEBUG_MODE = os.environ.get("CDP_DEBUG", "").lower() in ["true", "1", "yes"]
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)

# Detect script directory more robustly
script_dir = os.path.dirname(os.path.abspath(__file__))

# For CLI installations, the script might be in site-packages, so we need to find
# the actual source directory
def find_package_root():
    """Find the package root directory containing utils and core folders."""
    current_dir = script_dir
    max_attempts = 5  # Prevent infinite loops
    
    for _ in range(max_attempts):
        utils_path = os.path.join(current_dir, 'utils')
        core_path = os.path.join(current_dir, 'core')
        
        if os.path.exists(utils_path) and os.path.exists(core_path):
            return current_dir
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached filesystem root
            break
        current_dir = parent_dir
    
    return script_dir  # Fallback to script directory

package_root = find_package_root()

# Add package root to Python path early, before any imports
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# Also add utils and core directories directly to be extra sure
utils_path = os.path.join(package_root, 'utils')
core_path = os.path.join(package_root, 'core')
if os.path.exists(utils_path) and utils_path not in sys.path:
    sys.path.insert(0, utils_path)
if os.path.exists(core_path) and core_path not in sys.path:
    sys.path.insert(0, core_path)

# =============================================================================
# Dependency Validation - Check all required packages are available
# =============================================================================

try:
    # Import dependency validator first (it only uses standard library)
    import importlib.util
    validator_path = os.path.join(utils_path, 'dependency_validator.py')
    spec = importlib.util.spec_from_file_location("dependency_validator", validator_path)
    if spec and spec.loader:
        dependency_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dependency_validator)
        
        # Perform dependency validation - exits with helpful message if dependencies missing
        dependency_validator.validate_dependencies_with_helpful_exit()
        
        # Also check if installation might be out of date
        dependency_validator.check_installation_currency()
    else:
        print("Warning: Could not load dependency validator")
except Exception as dep_error:
    print(f"Warning: Could not validate dependencies: {dep_error}")
    # Continue anyway - the import section below will catch specific issues

# Import our modular components
try:
    # Try relative imports first (when installed as package)
    from .utils.user_interface import msg, UserMessenger, ProgressBar, menu
    from .utils.validators import InputValidator
    from .utils.csv_handler import CSVProcessor
    from .core.secure_token_manager import SecureTokenManager
    from .core.models import DocumentResult, FolderInfo
except ImportError:
    # Fallback to absolute imports (when run directly or CLI)
    try:
        from utils.user_interface import msg, UserMessenger, ProgressBar, menu
        from utils.validators import InputValidator
        from utils.csv_handler import CSVProcessor
        from core.secure_token_manager import SecureTokenManager
        from core.models import DocumentResult, FolderInfo
    except ImportError as e:
        # Final fallback - try importing directly from found paths
        try:
            import importlib.util
            import types
            
            # Load modules manually
            def load_module_from_file(module_name, file_path):
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
                return None
            
            # Load user_interface module
            ui_file = os.path.join(utils_path, 'user_interface.py')
            ui_module = load_module_from_file('user_interface', ui_file)
            if ui_module:
                msg = ui_module.msg
                UserMessenger = ui_module.UserMessenger
                ProgressBar = ui_module.ProgressBar
                menu = ui_module.menu
            else:
                raise ImportError("Could not load user_interface module")
            
            # Load other modules
            validators_file = os.path.join(utils_path, 'validators.py')
            validators_module = load_module_from_file('validators', validators_file)
            if validators_module:
                InputValidator = validators_module.InputValidator
            else:
                raise ImportError("Could not load validators module")
            
            csv_file = os.path.join(utils_path, 'csv_handler.py')
            csv_module = load_module_from_file('csv_handler', csv_file)
            if csv_module:
                CSVProcessor = csv_module.CSVProcessor
            else:
                raise ImportError("Could not load csv_handler module")
            
            token_file = os.path.join(core_path, 'secure_token_manager.py')
            token_module = load_module_from_file('secure_token_manager', token_file)
            if token_module:
                SecureTokenManager = token_module.SecureTokenManager
            else:
                raise ImportError("Could not load secure_token_manager module")
            
            models_file = os.path.join(core_path, 'models.py')
            models_module = load_module_from_file('models', models_file)
            if models_module:
                DocumentResult = models_module.DocumentResult
                FolderInfo = models_module.FolderInfo
            else:
                raise ImportError("Could not load models module")
            
        except Exception as manual_load_error:
            # Enhanced error message with dependency guidance
            print("\n" + "="*80)
            print("🔴 IMPORT ERROR - Failed to Load CDP Runbooker Components")
            print("="*80)
            print()
            print("This error typically occurs when:")
            print("1. You pulled updates that added new dependencies")
            print("2. Required packages are missing or outdated")
            print("3. The installation is incomplete or corrupted")
            print()
            print("📦 Error Details:")
            print(f"  • Import error: {e}")
            print(f"  • Manual load error: {manual_load_error}")
            print()
            print("💡 RECOMMENDED FIXES:")
            print("1. Reinstall/update all dependencies:")
            print(f"   cd {package_root}")
            print("   pip install -e .")
            print()
            print("2. If that doesn't work, try a clean reinstall:")
            print("   pip uninstall cdp-runbooker")
            print(f"   cd {package_root}")
            print("   pip install -e .")
            print()
            print("3. Ensure you're using Python 3.7+ and have network access")
            print()
            print("🔍 Debug Information:")
            print(f"  • Script directory: {script_dir}")
            print(f"  • Package root: {package_root}")
            print(f"  • Utils path exists: {os.path.exists(utils_path)}")
            print(f"  • Core path exists: {os.path.exists(core_path)}")
            print(f"  • Working directory: {os.getcwd()}")
            print()
            print("📚 For more help, see the troubleshooting section in README.md")
            print("="*80)
            raise ImportError("CDP Runbooker component loading failed - see error details above")

# =============================================================================
# Application Constants
# =============================================================================

# Application metadata
__version__ = "2.0.0"
__author__ = "fieldinn@"
__maintainer__ = "Product Operations TPM team"

# =============================================================================
# Configuration
# =============================================================================

class CDPConfig:
    """Configuration constants for the CDP Runbooker."""
    
    # Template IDs
    CORE_TEMPLATE_ID = "q6GTAa8WQAua"
    ENGAGEMENT_LOG_TEMPLATE_ID = "9oNTAMHiHeiN"
    
    # Folder IDs
    BASE_FOLDER_ID = "GnqeOTObOTLj"
    TEST_FOLDER_ID = "LCqeOdDHPHvy"
    USE_CASE_TEMPLATES_FOLDER_ID = "ZXDNOGbEqnFA"
    
    # Default folder IDs to try for CSV operations
    DEFAULT_CSV_FOLDER_IDS = ["4wX0O30tDBmU", "GnqeOTObOTLj"]
    
    # Rate limiting and retry settings
    MAX_RETRIES = 3
    BATCH_SIZE = 50
    RATE_LIMIT_DELAY = 1.0
    
    # API settings
    QUIP_BASE_URL = "https://platform.quip-amazon.com"
    TIMEOUT_CONNECT = 10
    TIMEOUT_READ = 90

# =============================================================================
# Core Application Classes
# =============================================================================

class QuipAPIClient:
    """Simplified Quip API client focused on core operations."""
    
    def __init__(self):
        """Initialize the Quip API client."""
        try:
            # Use the new secure token manager - it already validates the token
            secure_token_manager = SecureTokenManager()
            self.token, self.user_info = secure_token_manager.get_validated_token()
            
            # Log successful authentication for debugging
            logger.debug(f"Successfully authenticated as: {self.user_info.get('name', 'Unknown')}")
            
            self.client = self._initialize_client()
            self._setup_rate_limiting()
            
        except Exception as e:
            # Log detailed error information to workspace
            self._log_initialization_error(e)
            msg.print_error(f"Failed to initialize Quip client: {str(e)}")
            raise
    
    def _initialize_client(self):
        """Initialize the Quip client with proper configuration."""
        try:
            # Import Quip client
            try:
                import amazoncerts
                import quip
            except ImportError:
                import quipclient as quip
            
            client = quip.QuipClient(
                access_token=self.token,
                base_url=CDPConfig.QUIP_BASE_URL
            )
            
            # Configure requests session
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry_strategy = Retry(
                total=CDPConfig.MAX_RETRIES,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            session.timeout = (CDPConfig.TIMEOUT_CONNECT, CDPConfig.TIMEOUT_READ)
            
            client.request_session = session
            return client
            
        except Exception as e:
            raise Exception(f" Failed to initialize Quip client: {str(e)}")
    
    def _setup_rate_limiting(self):
        """Set up rate limiting tracking."""
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.rate_limit_limit = None
    
    def _log_initialization_error(self, error: Exception):
        """Log detailed initialization error information to workspace."""
        import platform
        from datetime import datetime
        
        # Create error log in current working directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"cdp-runbooker-error-{timestamp}.log"
        
        # Collect environment information
        env_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": os.getcwd(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "debug_mode": DEBUG_MODE
        }
        
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write("=== CDP Runbooker Initialization Error Log ===\n\n")
                for key, value in env_info.items():
                    f.write(f"{key}: {value}\n")
                f.write(f"\nFull traceback:\n{traceback.format_exc()}\n")
            
            logger.error(f"Detailed error log saved to: {log_filename}")
            
        except Exception as log_error:
            logger.warning(f"Could not save error log: {str(log_error)}")
    
    
    def verify_credentials(self) -> bool:
        """Verify API credentials are valid."""
        try:
            # We already validated the token during initialization
            # Just return True since we have valid user_info
            if hasattr(self, 'user_info') and self.user_info:
                return True
            else:
                # Fallback to testing the client if user_info is not available
                user = self.client.get_authenticated_user()
                msg.print_info(f" Authenticated as: {user.get('name', 'Unknown')}")
                return True
        except Exception as e:
            msg.print_error(f" Authentication failed: {str(e)}")
            return False


class DocumentManager:
    """Handles document creation and management operations."""
    
    def __init__(self, client: QuipAPIClient):
        """Initialize with a Quip API client."""
        self.client = client
    
    def create_core_runbook(self, folder_id: str, folder_name: str, customer_name: str) -> DocumentResult:
        """Create a core CDP runbook with engagement log."""
        msg.print_step(1, "Creating core CDP runbook")
        
        # Create main runbook
        main_thread_id = self._create_document_from_template(
            folder_id=folder_id,
            title=f"{folder_name}_Runbook-Core",
            template_id=CDPConfig.CORE_TEMPLATE_ID,
            customer_name=customer_name
        )
        
        # Create engagement log
        msg.print_step(2, "Creating engagement log")
        log_thread_id = self._create_document_from_template(
            folder_id=folder_id,
            title=f"{folder_name}_Engagement Log",
            template_id=CDPConfig.ENGAGEMENT_LOG_TEMPLATE_ID,
            customer_name=customer_name
        )
        
        # Prepare result
        documents = {
            "Core Runbook": f"https://quip-amazon.com/{main_thread_id}",
            "Engagement Log": f"https://quip-amazon.com/{log_thread_id}"
        }
        
        return DocumentResult(main_thread_id=main_thread_id, documents=documents)
    
    def create_use_case_runbook(self, folder_id: str, folder_name: str, 
                               template_id: str, use_case_name: str, customer_name: str) -> DocumentResult:
        """Create a use-case specific runbook."""
        msg.print_step(3, f"Creating use-case runbook: {use_case_name}")
        
        thread_id = self._create_document_from_template(
            folder_id=folder_id,
            title=f"{folder_name}_Runbook-Use-case-{use_case_name}",
            template_id=template_id,
            customer_name=customer_name
        )
        
        documents = {
            "Use-case Runbook": f"https://quip-amazon.com/{thread_id}"
        }
        
        return DocumentResult(main_thread_id=thread_id, documents=documents)
    
    def _create_document_from_template(self, folder_id: str, title: str, 
                                     template_id: str, customer_name: str) -> str:
        """Create a document from a template with retry logic."""
        import requests
        import time
        
        for attempt in range(CDPConfig.MAX_RETRIES):
            try:
                # Prepare request data
                post_data = {
                    'folder_id': folder_id,
                    'title': title,
                    'copy_annotations': True,
                    'mail_merge_values': {
                        "Customer": {"Name": customer_name},
                        "Date": datetime.now().strftime("%Y-%m-%d")
                    },
                    'member_ids': [self.client.client.get_authenticated_user()['id']],
                    'type': 'document'
                }
                
                # Make request
                url = f"{self.client.client.base_url}/2/threads/{template_id}/copy"
                headers = {
                    'Authorization': f'Bearer {self.client.token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                response = requests.post(url, headers=headers, json=post_data, 
                                       timeout=(CDPConfig.TIMEOUT_CONNECT, CDPConfig.TIMEOUT_READ))
                
                if response.status_code == 500:
                    if attempt < CDPConfig.MAX_RETRIES - 1:
                        wait_time = (attempt + 1) * 2
                        msg.print_warning(f" Server error, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(" Server error after all retries")
                
                response.raise_for_status()
                data = response.json()
                thread_id = data['thread']['id']
                
                msg.print_success(f" Created document: {title}")
                return thread_id
                
            except Exception as e:
                if attempt < CDPConfig.MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 2
                    msg.print_warning(f" Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f" Failed to create document after {CDPConfig.MAX_RETRIES} attempts: {str(e)}")
    
    def download_document(self, thread_id: str) -> str:
        """Download a document as HTML."""
        try:
            thread = self.client.client.get_thread(thread_id)
            html_content = thread['html']
            title = thread['thread']['title']
            
            # Save to downloads
            import pathlib
            downloads_dir = pathlib.Path.home() / 'Downloads'
            downloads_dir.mkdir(exist_ok=True)
            
            safe_title = InputValidator.sanitize_filename(title)
            html_path = downloads_dir / f"{safe_title}.html"
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            msg.print_success(f" Downloaded: {title}")
            return str(html_path)
            
        except Exception as e:
            raise Exception(f" Failed to download document: {str(e)}")


class FolderManager:
    """Handles folder operations."""
    
    def __init__(self, client: QuipAPIClient):
        """Initialize with a Quip API client."""
        self.client = client
    
    def create_engagement_folder(self, customer_name: str, engagement_name: str, 
                               start_month: str, sim_id: str = "", is_test: bool = False) -> FolderInfo:
        """Create a CDP engagement folder."""
        try:
            # Construct folder name
            folder_name = f"CDP_{start_month}_{customer_name}_{engagement_name}"
            if sim_id:
                folder_name = f"{folder_name}_{sim_id}"
            
            # Determine parent folder
            parent_id = CDPConfig.TEST_FOLDER_ID if is_test else CDPConfig.BASE_FOLDER_ID
            
            # Get current user
            current_user = self.client.client.get_authenticated_user()
            member_ids = [current_user['id']]
            
            # Create folder
            response = self.client.client.new_folder(
                title=folder_name,
                parent_id=parent_id,
                member_ids=member_ids
            )
            
            folder_id = response['folder']['id']
            folder_url = f"https://quip-amazon.com/{folder_id}"
            
            msg.print_success(f" Created folder: {folder_name}")
            
            return FolderInfo(
                folder_id=folder_id,
                folder_name=folder_name,
                folder_url=folder_url
            )
            
        except Exception as e:
            raise Exception(f" Failed to create folder: {str(e)}")
    
    def list_use_case_templates(self) -> list:
        """List available use-case templates."""
        try:
            folder_info = self.client.client.get_folder(CDPConfig.USE_CASE_TEMPLATES_FOLDER_ID)
            
            if 'children' not in folder_info:
                return []
            
            templates = []
            for idx, child in enumerate(folder_info['children'], 1):
                if 'thread_id' in child:
                    thread_id = child['thread_id']
                    thread_info = self.client.client.get_thread(thread_id)
                    
                    if 'thread' in thread_info and 'title' in thread_info['thread']:
                        title = thread_info['thread']['title']
                        templates.append((idx, title, thread_id))
            
            return templates
            
        except Exception as e:
            raise Exception(f" Failed to list templates: {str(e)}")


class CSVUserManager:
    """Handles CSV user operations."""
    
    def __init__(self, client: QuipAPIClient):
        """Initialize with a Quip API client."""
        self.client = client
        # Setup rate limiting tracking
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.rate_limit_limit = None
    
    def add_users_from_csv(self, folder_id: str, csv_path: str, debug_mode: bool = False) -> bool:
        """
        Add users from a CSV file to a Quip folder using efficient bulk lookups
        
        Args:
            folder_id (str): The ID of the folder to add users to
            csv_path (str): Path to the CSV file containing user information
            debug_mode (bool): If True, print verbose debugging information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            local_debug = debug_mode
            
            logger.info(f" Adding users from CSV file: {csv_path} to folder ID: {folder_id}")
            
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f" CSV file not found: {csv_path}")
            
            # Verify folder ID format
            if not re.match(r'^[a-zA-Z0-9]{10,}$', folder_id):
                logger.warning(f" Folder ID '{folder_id}' doesn't match expected format. Continuing anyway...")
            
            # Get current folder info to verify access
            try:
                folder_info = self.client.client.get_folder(folder_id)
            except Exception as e:
                logger.error(f" Error retrieving folder information: {str(e)}")
                msg.print_error(f" Could not access folder with ID '{folder_id}'")
                msg.print_info("Please check if the folder ID is correct and you have access to it.")
                return False
            
            if 'folder' not in folder_info:
                logger.error(f" Invalid folder information returned from API: {folder_info}")
                msg.print_error("Invalid folder information returned from Quip API")
                return False
            
            # Step 1: Extract all emails from CSV file
            msg.print_step(1, "Extracting emails from CSV file")
            emails = CSVProcessor.extract_emails_from_csv(csv_path, debug_mode=local_debug)
            
            if not emails:
                logger.warning("No valid emails found in CSV file")
                msg.print_error("No valid emails found in the CSV file.")
                msg.print_info("Please check the file format and ensure it contains valid email information.")
                return False
            
            logger.info(f" Extracted {len(emails)} emails from CSV file")
            
            # Step 2: Get existing folder member IDs
            msg.print_step(2, "Getting existing folder members")
            existing_member_ids = set()
            
            if 'member_ids' in folder_info:
                existing_member_ids = set(folder_info['member_ids'])
                logger.info(f" Found {len(existing_member_ids)} existing folder members")
            else:
                logger.warning("Could not retrieve existing folder member IDs from folder info")
                msg.print_warning("Cannot retrieve existing folder members.")
                msg.print_info("This means the script cannot check for duplicates.")
                
                # Ask user if they want to continue
                try:
                    response = msg.get_user_choice("Do you want to continue anyway?", ["y", "n"])
                    if response not in ['y', 'yes']:
                        msg.print_info("Operation cancelled by user.")
                        return False
                except KeyboardInterrupt:
                    msg.print_error("Operation cancelled by user.")
                    return False
            
            # Step 3: Bulk resolve CSV emails to member IDs
            msg.print_step(3, "Bulk resolving emails to member IDs")
            
            # Create progress bar for email resolution
            resolution_progress = ProgressBar(len(emails), "Resolving emails")
            resolution_progress.update(0, "Starting email resolution...")
            
            email_to_member_id, failed_emails = self._resolve_emails_to_member_ids(emails, debug_mode=local_debug, progress_bar=resolution_progress)
            
            resolution_progress.complete("Email resolution complete!")
            
            # Step 4: Filter out existing members
            msg.print_step(4, "Filtering out existing members")
            new_member_ids = []
            already_member_emails = []
            
            for email, member_id in email_to_member_id.items():
                if member_id in existing_member_ids:
                    already_member_emails.append(email)
                else:
                    new_member_ids.append(member_id)
            
            logger.info(f" Found {len(new_member_ids)} new members to add, {len(already_member_emails)} already members")
            
            # Step 5: Add new members to folder
            added_count = 0
            error_count = 0
            
            if new_member_ids:
                msg.print_step(5, "Adding new members to folder")
                
                # Add members in batches to handle large lists and rate limiting
                batch_size = CDPConfig.BATCH_SIZE  # Conservative batch size
                for i in range(0, len(new_member_ids), batch_size):
                    batch_member_ids = new_member_ids[i:i+batch_size]
                    
                    try:
                        # Add delay between batches for rate limiting
                        if i > 0:
                            time.sleep(CDPConfig.RATE_LIMIT_DELAY)
                        
                        logger.info(f" Adding batch {i//batch_size + 1}/{(len(new_member_ids) + batch_size - 1)//batch_size} ({len(batch_member_ids)} members)")
                        
                        # Use standard client method directly (skipping the direct API that fails)
                        try:
                            self.client.client.add_folder_members(folder_id, batch_member_ids)
                            added_count += len(batch_member_ids)
                            logger.info(f" Successfully added batch of {len(batch_member_ids)} members")
                        except Exception as e:
                            error_str = str(e).lower()
                            
                            # Handle rate limiting
                            if '429' in error_str or 'rate limit' in error_str:
                                logger.warning(f" Rate limit hit for batch {i//batch_size + 1}, waiting and retrying...")
                                time.sleep(5)
                                try:
                                    self.client.client.add_folder_members(folder_id, batch_member_ids)
                                    added_count += len(batch_member_ids)
                                    logger.info(f" Successfully added batch of {len(batch_member_ids)} members after retry")
                                except Exception as retry_e:
                                    logger.error(f" Failed to add batch {i//batch_size + 1} after retry: {str(retry_e)}")
                                    error_count += len(batch_member_ids)
                            else:
                                logger.error(f" Failed to add batch {i//batch_size + 1}: {str(e)}")
                                error_count += len(batch_member_ids)
                    except Exception as e:
                        logger.error(f" Unexpected error processing batch: {str(e)}")
                        error_count += len(batch_member_ids)
            
            # Step 6: Generate comprehensive results
            msg.print_step(6, "Generating results summary")
            
            total_csv_emails = len(emails)
            resolved_emails = len(email_to_member_id)
            skipped_already_members = len(already_member_emails)
            failed_to_resolve = len(failed_emails)
            
            # Print detailed summary for user
            summary_items = {
                "📄 Total emails in CSV": total_csv_emails,
                "✅ Successfully resolved": resolved_emails,
                "⚠️ Already members (skipped)": skipped_already_members,
                "❌ Failed to resolve": failed_to_resolve,
                "➕ Successfully added": added_count
            }
            if error_count > 0:
                summary_items["🔴 Errors during addition"] = error_count
                
            msg.print_summary("User Addition Summary", summary_items)
            
            # Show failed emails if any
            if failed_emails:
                msg.print_error("Failed to resolve these emails:")
                for email in failed_emails[:10]:  # Show first 10
                    print(f"   - {email}")
                if len(failed_emails) > 10:
                    print(f"   ... and {len(failed_emails) - 10} more")
                msg.print_info("These emails may not exist in the Quip system or may have different domain variations.")
            
            return added_count > 0 or skipped_already_members > 0
            
        except Exception as e:
            logger.error(f" Failed to add users from CSV: {str(e)}")
            if local_debug:
                logger.debug(f" CSV processing traceback: {traceback.format_exc()}")
            msg.print_error(f" Error adding users: {str(e)}")
            return False
    
    def _add_members_direct_api(self, folder_id: str, member_ids: list) -> dict:
        """
        Add members to a folder using direct API call.
        
        Args:
            folder_id (str): The ID of the folder
            member_ids (list): List of member IDs to add
            
        Returns:
            dict: Response data or success indicator
            
        Raises:
            Exception: If the API call fails
        """
        import requests
        
        headers = {
            'Authorization': f'Bearer {self.client.token}',
            'Content-Type': 'application/json'
        }
        
        # Use the correct Quip API endpoint for adding folder members
        # The correct endpoint is PUT /1/folders/{folder_id} with member_ids in the data
        url = f"{self.client.client.base_url}/1/folders/{folder_id}"
        
        # Get current folder info first to preserve existing members
        try:
            folder_info = self.client.client.get_folder(folder_id)
            existing_member_ids = folder_info.get('member_ids', [])
            
            # Combine existing and new member IDs
            all_member_ids = list(set(existing_member_ids + member_ids))
            
        except Exception as e:
            logger.warning(f" Could not get existing members, proceeding with just new members: {str(e)}")
            all_member_ids = member_ids
        
        data = {"member_ids": all_member_ids}
        
        response = requests.put(
            url, 
            headers=headers, 
            json=data, 
            timeout=(CDPConfig.TIMEOUT_CONNECT, CDPConfig.TIMEOUT_READ)
        )
        
        if response.status_code in [200, 204]:
            return response.json() if response.content else {"success": True}
        else:
            error_msg = response.text
            raise Exception(f" API error: {response.status_code} - {error_msg}")
    
    def _resolve_emails_to_member_ids(self, emails: list, debug_mode: bool = False, progress_bar: ProgressBar = None) -> tuple:
        """
        Resolve a list of email addresses to Quip member IDs.
        
        Args:
            emails (list): List of email addresses
            debug_mode (bool): Enable debug logging
            progress_bar (ProgressBar): Optional progress bar for tracking
            
        Returns:
            tuple: (successful_mappings dict, failed_emails list)
                - successful_mappings: {email: member_id}
                - failed_emails: [emails that couldn't be resolved]
        """
        import time
        import requests
        
        email_to_member_id = {}
        failed_emails = []
        
        # Phase 1: Try all emails exactly as written in bulk calls
        logger.info("Phase 1: Looking up emails as provided...")
        remaining_emails = list(set(emails))  # Remove duplicates
        
        # Update progress bar for phase 1 start
        if progress_bar:
            progress_bar.update(0, "Phase 1: Bulk email lookup")
        
        # Process in batches of 1000 (API limit)
        total_batches = (len(remaining_emails) + 999) // 1000
        for i in range(0, len(remaining_emails), 1000):
            batch_emails = remaining_emails[i:i+1000]
            current_batch = i // 1000 + 1
            
            # Update progress bar
            if progress_bar:
                progress_completed = (current_batch - 1) / total_batches * 0.7  # Phase 1 is 70% of the work
                progress_bar.update(int(progress_completed * len(emails)), f"Batch {current_batch}/{total_batches}")
            
            try:
                ids_param = ','.join(batch_emails)
                url = f"{self.client.client.base_url}/1/users/"
                headers = {
                    'Authorization': f'Bearer {self.client.token}',
                    'Accept': 'application/json'
                }
                params = {'ids': ids_param}
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    timeout=(CDPConfig.TIMEOUT_CONNECT, CDPConfig.TIMEOUT_READ)
                )
                response.raise_for_status()
                
                users_data = response.json()
                
                # Process successful lookups
                for email in batch_emails:
                    if email in users_data and isinstance(users_data[email], dict) and 'id' in users_data[email]:
                        member_id = users_data[email]['id']
                        email_to_member_id[email] = member_id
                
            except Exception as e:
                logger.warning(f" Phase 1 batch {i//1000 + 1} failed: {str(e)}")
                continue
        
        # Identify emails that failed in Phase 1
        phase1_successful = set(email_to_member_id.keys())
        phase1_failed = [email for email in remaining_emails if email not in phase1_successful]
        
        logger.info(f" Phase 1 complete: {len(phase1_successful)} found, {len(phase1_failed)} need domain fallback")
        
        # Phase 2: For failed emails, try different domain variations
        if phase1_failed:
            logger.info("Phase 2: Trying domain variations for failed emails...")
            
            # Update progress bar for phase 2
            if progress_bar:
                progress_bar.update(int(0.7 * len(emails)), "Phase 2: Domain variations")
            
            # Amazon email domains in priority order
            amazon_domains = [
                'amazon.com', 'amazon.co.jp', 'amazon.fr', 'amazon.co.uk', 
                'amazon.com.au', 'amazon.de', 'amazon.es', 'amazon.it'
                # Add more domains as needed
            ]
            
            # Process each failed email with progress tracking
            for idx, email in enumerate(phase1_failed):
                # Update progress bar periodically
                if progress_bar and idx % 10 == 0:  # Update every 10 emails
                    phase2_progress = 0.7 + (idx / len(phase1_failed)) * 0.3  # Phase 2 is remaining 30%
                    progress_bar.update(int(phase2_progress * len(emails)), f"Checking domain variations: {idx}/{len(phase1_failed)}")
                
                if '@' in email:
                    # Extract username from email
                    username = email.split('@')[0]
                    
                    # Try different domains
                    for domain in amazon_domains:
                        variation = f"{username}@{domain}"
                        try:
                            user_info = self.client.client.get_user(variation)
                            if user_info and 'id' in user_info:
                                email_to_member_id[email] = user_info['id']
                                break  # Found a match, move to the next email
                        except:
                            continue  # Try next domain
                
                # If still not resolved, add to failed emails
                if email not in email_to_member_id:
                    failed_emails.append(email)
            
            # Final progress update for phase 2
            if progress_bar:
                progress_bar.update(len(emails), "Domain variations complete")
        
        logger.info(f" Email resolution complete: {len(email_to_member_id)} successful, {len(failed_emails)} failed")
        return email_to_member_id, failed_emails


# =============================================================================
# Main Application Logic
# =============================================================================

class CDPRunbookApp:
    """Main application class that orchestrates all operations."""
    
    def __init__(self):
        """Initialize the application."""
        self.client = QuipAPIClient()
        self.document_manager = DocumentManager(self.client)
        self.folder_manager = FolderManager(self.client)
        self.csv_manager = CSVUserManager(self.client)
    
    def create_core_runbook_workflow(self):
        """Handle the core runbook creation workflow."""
        msg.print_header("Core CDP Runbook Creation")
        
        # Get user inputs
        customer_name = self._get_validated_input("Enter Customer Name", "CustomerName")
        engagement_name = self._get_validated_input("Enter Engagement Short Name", "EngagementName")
        start_month = self._get_date_input("Enter Engagement Start Month (YYYY-MM)")
        sim_id = self._get_sim_id()
        is_test = self._get_test_folder_preference()
        
        try:
            # Create folder
            folder_info = self.folder_manager.create_engagement_folder(
                customer_name, engagement_name, start_month, sim_id, is_test
            )
            
            # Create documents
            document_result = self.document_manager.create_core_runbook(
                folder_info.folder_id, folder_info.folder_name, customer_name
            )
            
            # Display results
            self._display_success_summary(folder_info, document_result.documents)
            
        except Exception as e:
            msg.print_error(f" Failed to create core runbook: {str(e)}")
            raise
    
    def create_use_case_runbook_workflow(self):
        """Handle the use-case runbook creation workflow."""
        msg.print_header("Use-case Specific Runbook Creation")
        
        try:
            # Get available templates
            templates = self.folder_manager.list_use_case_templates()
            if not templates:
                msg.print_error("No use-case templates found")
                return
            
            # Display templates and get user selection
            msg.print_info("Available Use-case Templates:")
            for idx, title, _ in templates:
                print(f"{idx}. {title}")
            
            selected_template = self._get_template_selection(templates)
            _, selected_title, selected_thread_id = selected_template
            
            # Get user inputs
            customer_name = self._get_validated_input("Enter Customer Name", "CustomerName")
            engagement_name = self._get_validated_input("Enter Engagement Short Name", "EngagementName")
            start_month = self._get_date_input("Enter Engagement Start Month (YYYY-MM)")
            sim_id = self._get_sim_id()
            is_test = self._get_test_folder_preference()
            
            # Create folder
            folder_info = self.folder_manager.create_engagement_folder(
                customer_name, engagement_name, start_month, sim_id, is_test
            )
            
            # Create core runbook first
            core_result = self.document_manager.create_core_runbook(
                folder_info.folder_id, folder_info.folder_name, customer_name
            )
            
            # Create use-case runbook
            use_case_name = self._extract_use_case_name(selected_title)
            use_case_result = self.document_manager.create_use_case_runbook(
                folder_info.folder_id, folder_info.folder_name, 
                selected_thread_id, use_case_name, customer_name
            )
            
            # Combine all documents
            all_documents = {**core_result.documents, **use_case_result.documents}
            
            # Display results
            self._display_success_summary(folder_info, all_documents)
            
        except Exception as e:
            msg.print_error(f" Failed to create use-case runbook: {str(e)}")
            raise
    
    def download_document_workflow(self, thread_id: str):
        """Handle document download workflow."""
        try:
            html_path = self.document_manager.download_document(thread_id)
            msg.print_success(f" Document downloaded to: {html_path}")
        except Exception as e:
            msg.print_error(f" Failed to download document: {str(e)}")
            raise
    
    def add_users_workflow(self, csv_path: str, folder_id: str = None, debug_mode: bool = False):
        """Handle CSV user addition workflow."""
        try:
            # Use provided folder ID or try defaults
            if folder_id:
                folder_ids = [folder_id]
            else:
                folder_ids = CDPConfig.DEFAULT_CSV_FOLDER_IDS
            
            success = False
            for folder_id in folder_ids:
                msg.print_info(f" Trying folder ID: {folder_id}")
                if self.csv_manager.add_users_from_csv(folder_id, csv_path, debug_mode):
                    success = True
                    break
            
            if not success:
                msg.print_error("Failed to add users with all folder IDs")
                
        except Exception as e:
            msg.print_error(f" Failed to add users: {str(e)}")
            raise
    
    # Helper methods
    def _get_validated_input(self, prompt: str, field_name: str) -> str:
        """Get validated user input."""
        while True:
            value = msg.get_user_input(prompt)
            if not value:
                msg.print_warning(f" Empty {field_name} provided. Please try again.")
                continue
            if not InputValidator.validate_folder_name(value):
                msg.print_warning(f" Invalid characters in {field_name}. Please avoid special characters.")
                continue
            return value
    
    def _get_date_input(self, prompt: str) -> str:
        """Get and validate date input."""
        current_month = datetime.now().strftime('%Y-%m')
        full_prompt = f"{prompt} (press Enter for current month {current_month})"
        
        while True:
            value = msg.get_user_input(full_prompt, required=False)
            if not value:
                return current_month
            if InputValidator.validate_date_format(value):
                return value
            msg.print_warning("Invalid date format. Please use YYYY-MM format.")
    
    def _get_sim_id(self) -> str:
        """Get and validate SIM ID."""
        while True:
            value = msg.get_user_input("Enter CDP Engagement SIM ID or press Enter to skip", required=False)
            if not value:
                return ""
            
            formatted_id = InputValidator.validate_sim_id(value)
            if formatted_id is None:
                msg.print_error("Invalid SIM ID format. Please try again.")
                continue
            
            confirm = msg.get_user_choice(f"Confirm SIM ID: {formatted_id}", ["y", "n"], "y")
            if confirm in ['y', 'yes']:
                return formatted_id
    
    def _get_test_folder_preference(self) -> bool:
        """Ask if user is creating a test folder."""
        response = msg.get_user_choice("Are you creating this for testing purposes?", ["y", "n"], "n")
        return response in ['y', 'yes']
    
    def _get_template_selection(self, templates: list) -> tuple:
        """Get user's template selection."""
        while True:
            try:
                selection = int(msg.get_user_input("Enter the number of the template to use"))
                if 1 <= selection <= len(templates):
                    return templates[selection - 1]
                else:
                    msg.print_warning(f" Please enter a number between 1 and {len(templates)}")
            except ValueError:
                msg.print_warning("Please enter a valid number")
    
    def _extract_use_case_name(self, template_title: str) -> str:
        """Extract use-case name from template title."""
        name = template_title
        for prefix in ["[WIP] - ", "CDP - ", "CDP "]:
            name = name.replace(prefix, "")
        for suffix in [" - Runbook Template", " Runbook Template", " Template"]:
            name = name.replace(suffix, "")
        return name.strip()
    
    def _display_success_summary(self, folder_info: FolderInfo, documents: dict):
        """Display a formatted success summary."""
        msg.print_success("CDP Runbook creation completed successfully!")
        
        print(f"\n┌─ Summary ──────────────────────────────────────────────────┐")
        print(f"│ Engagement: {folder_info.folder_name}")
        print(f"│ Status: ✓ Successfully Created")
        print(f"│")
        print(f"│ 📁 Folder URL:")
        print(f"│    {folder_info.folder_url}")
        print(f"│")
        print(f"│ 📄 Document URLs:")
        for doc_name, doc_url in documents.items():
            print(f"│    • {doc_name}:")
            print(f"│      {doc_url}")
        print(f"└────────────────────────────────────────────────────────────┘")
        
        msg.print_success("Your files are ready!")


# =============================================================================
# Application Health and Diagnostics
# =============================================================================

def get_application_info() -> dict:
    """Get application metadata and runtime information."""
    return {
        "name": "CDP Runbook Creator",
        "version": __version__,
        "author": __author__,
        "maintainer": __maintainer__,
        "python_version": sys.version,
        "debug_mode": DEBUG_MODE
    }

def setup_signal_handlers():
    """Set up graceful signal handling for clean shutdown."""
    def signal_handler(signum, frame):
        """Handle interrupt signals gracefully."""
        print("\n\n🔄 CDP Runbooker shutting down gracefully...")
        print("✅ Your secure tokens remain encrypted and protected.")
        sys.exit(0)
    
    # Register signal handlers for interrupts
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# =============================================================================
# Main Entry Point
# =============================================================================

def display_banner():
    """Display the application banner."""
    banner = """
╔██████╗██████╗ ██████╗     ██████╗ ██╗   ██╗███╗   ██╗██████╗ ╔██████╗ ╔██████╗ ██╗  ██╗███████╗██████╗ 
██╔════╝██╔══██╗██╔══██╗    ██╔══██╗██║   ██║████╗  ██║██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗
██║     ██║  ██║██████╔╝    ██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║   ██║██║   ██║█████╔╝ █████╗  ██████╔╝
██║     ██║  ██║██╔═══╝     ██╔══██╗██║   ██║██║╚██╗██║██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
╚██████╗██████╔╝██║         ██║  ██║╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝╚██████╔╝██║  ██╗███████╗██║  ██║
 ╚═════╝╚═════╝ ╚═╝         ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                Countdown Premium (CDP) Runbook Creator                                   ║
║                             Created by fieldinn@ with the help of _Cline_                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    """
    try:
        print(banner)
    except UnicodeEncodeError:
        print("=== CDP RUNBOOKER 2.0! ===")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='CDP Runbooker')
    parser.add_argument('--download', type=str, help='Download a Quip doc by thread ID')
    parser.add_argument('--add-users', type=str, help='Add users to the CDP Engagements Quip folder from a CSV file')
    parser.add_argument('--folder-id', type=str, help='Alternate Folder ID for user addition')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--debug-report', action='store_true', help='Generate comprehensive debug report')
    parser.add_argument('--error-context', action='store_true', help='Include error context in debug report')
    parser.add_argument('--continue', dest='continue_after_debug', action='store_true', help='Continue with normal operation after generating debug report')
    parser.add_argument('--diagnose-token', type=str, nargs='?', const='stored', help='Diagnose token validation issues. Optionally provide a token to test.')
    return parser.parse_args()

def main():
    """Main application entry point."""
    display_banner()
    
    # Set up SSL certificates first
    setup_ssl_certificates()
    
    # Set up graceful signal handling
    setup_signal_handlers()
    
    # Configure logging
    level = logging.DEBUG if os.environ.get("CDP_DEBUG") else logging.INFO
    logging.basicConfig(
        format='%(asctime)s UTC %(levelname)s: %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        args = parse_arguments()
        
        # Handle debug report generation
        if args.debug_report:
            try:
                from utils.debug_reporter import generate_debug_report
                msg.print_header("Generating Debug Report")
                msg.print_info("Collecting comprehensive diagnostic information...")
                
                report_path = generate_debug_report(
                    error=None,
                    save_to_file=True,
                    output_dir=None
                )
                
                msg.print_success(f"Debug report generated: {report_path}")
                msg.print_info("Please review the report before sharing, as it may contain system information.")
                
                if not args.continue_after_debug:
                    msg.print_info("Debug report generation complete. Exiting.")
                    return
                    
            except Exception as e:
                msg.print_error(f"Failed to generate debug report: {str(e)}")
                if not args.continue_after_debug:
                    sys.exit(1)
        
        # Handle token diagnostics
        if args.diagnose_token is not None:
            try:
                # Don't need QuipAPIClient, just SecureTokenManager
                secure_token_manager = SecureTokenManager()
                
                # If 'stored' or no token provided, use stored token
                test_token = None if args.diagnose_token == 'stored' else args.diagnose_token
                
                # Run diagnostics
                result = secure_token_manager.diagnose_token(test_token)
                
                if not result:
                    sys.exit(1)
                else:
                    sys.exit(0)
                    
            except Exception as e:
                msg.print_error(f"Token diagnostics failed: {str(e)}")
                sys.exit(1)
        
        # Initialize the main application
        app = CDPRunbookApp()
        
        if args.download:
            # Download mode
            app.download_document_workflow(args.download)
            
        elif args.add_users:
            # CSV user addition mode
            app.add_users_workflow(args.add_users, args.folder_id, args.debug)
            
        else:
            # Interactive mode
            msg.print_header("CDP Runbook Creation")
            print("┌─ Select Runbook Type ─────────────────────────────────────┐")
            print("│  1. Core CDP Runbook                                      │")
            print("│  2. Use-case Specific Runbook                             │")
            print("└───────────────────────────────────────────────────────────┘")
            
            choice = msg.get_user_choice("Enter your choice", ["1", "2"])
            
            if choice == '1':
                app.create_core_runbook_workflow()
            else:
                app.create_use_case_runbook_workflow()
    
    except KeyboardInterrupt:
        msg.print_error("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        # Generate debug report on critical errors
        try:
            from utils.debug_reporter import generate_debug_report
            msg.print_error(f" Application failed: {str(e)}")
            msg.print_info("Generating debug report for troubleshooting...")
            
            report_path = generate_debug_report(
                error=e,
                save_to_file=True,
                output_dir=None
            )
            
            msg.print_info(f"Debug report saved to: {report_path}")
            msg.print_info("Please share this report when reporting the issue.")
            
        except Exception as debug_error:
            msg.print_warning(f"Could not generate debug report: {str(debug_error)}")
        
        sys.exit(1)

if __name__ == '__main__':
    main()
