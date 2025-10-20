# CDP Runbook Creator - Development Guide

This guide provides detailed information about the modular architecture, development practices, and contribution guidelines for the CDP Runbook Creator.

## 🏗️ Architecture Overview

The CDP Runbook Creator features a clean, modular architecture focused on maintainability and professional user experience.

### **Main Application**

| Component | Purpose |
|-----------|---------|
| `cdpRunbooker.py` | **Complete CDP Runbook Creator** ⭐ |
| | • Full-featured runbook creation |
| | • Progress bars and professional UI |
| | • Bulk user management capabilities |
| | • Intelligent error recovery |
| | • Clean, modular architecture |


### **Modular Structure**

```
src/CDP-Quip-Runbooker/
├── cdpRunbooker.py    # Main application entry point
├── core/                         # Core business logic
│   ├── __init__.py               # Module initialization
│   ├── models.py                 # Data models and structures
│   └── token_manager.py          # API token management
├── utils/                        # Utility modules
│   ├── __init__.py               # Module initialization
│   ├── csv_handler.py            # CSV processing utilities
│   ├── user_interface.py         # UI components and messaging
│   └── validators.py             # Input validation functions
├── Amazon-Teams-Member-Copier.js # Tampermonkey script for email extraction
├── requirements.txt              # Python dependencies
├── README.md                     # User documentation
└── DEVELOPMENT.md                # Development guide (this file)
```

## 🔧 Core Components

### **1. Configuration (`CDPConfig`)**
Central configuration management with constants for:
- Template IDs for different document types
- Folder IDs for various organizational structures
- API settings (timeouts, retry limits, rate limiting)
- Default configurations for CSV operations

### **2. API Client (`QuipAPIClient`)**
Simplified Quip API client with:
- Enhanced token validation during initialization
- Automatic retry logic with exponential backoff
- Rate limiting based on API response headers
- Session configuration with proper timeouts
- Error handling and authentication management

### **3. Token Management (`TokenManager`)**
Enhanced token management with:
- Automatic token validation by testing API calls
- Expired token detection and user guidance
- Interactive token renewal workflow
- Persistent storage to shell configuration files
- Graceful error handling and recovery

### **3. Document Management (`DocumentManager`)**
Handles all document operations:
- Template-based document creation with mail merge
- Retry logic for handling server errors (500 responses)
- HTML document downloads with proper filename sanitization
- Progress tracking for long operations

### **4. Folder Management (`FolderManager`)**
Manages Quip folder operations:
- CDP engagement folder creation with naming conventions
- Use-case template discovery and listing
- Folder structure validation and verification

### **5. CSV User Management (`CSVUserManager`)**
Bulk user operations with:
- **Phase 1**: Bulk email resolution (1000 users per API call)
- **Phase 2**: Domain fallback for failed emails (30+ Amazon domains)
- Progress tracking with real-time updates
- Comprehensive error reporting and recovery

### **6. Main Application (`CDPRunbookApp`)**
Orchestrates all workflows:
- Interactive menu-driven user experience
- Input validation and sanitization
- Workflow coordination between components
- Professional result presentation

## 🎨 User Interface Components

### **UserMessenger System**
Centralized messaging with:
- **Color-coded output**: Success (green), Warning (yellow), Error (red), Info (blue)
- **Consistent symbols**: ✅ ⚠️ ❌ ℹ️ 🔄 🎯 ▶️
- **Formatted headers and summaries**
- **Terminal capability detection** (respects `NO_COLOR` environment variable)

### **Progress Tracking**
```python
# Simple progress bar: [████████░░] 80% Processing...
progress = ProgressBar(total=100, description="Processing emails")
progress.update(current=80, status="Resolving domains")
progress.complete("Email resolution complete!")
```

### **Menu System**
```python
# Consistent boxed menus
menu.display_boxed_menu(
    title="CDP Runbook Creation",
    options=["Core CDP Runbook", "Use-case Specific Runbook"],
    current_step=1,
    total_steps=3
)
```

## 🔐 Token Validation System

### **Validation Process**
1. **Existence Check**: Verify token exists in environment or config files
2. **API Validation**: Test token by calling `get_authenticated_user()`
3. **Expiration Detection**: Catch 401 errors indicating expired tokens
4. **Renewal Workflow**: Guide user through getting new token
5. **Persistent Storage**: Save new tokens to appropriate shell config

### **Implementation Details**
```python
@staticmethod
def get_validated_token() -> Tuple[str, dict]:
    """
    Get and validate API token, handling expired tokens gracefully.
    
    Returns:
        tuple: (token, user_info) if valid
        
    Raises:
        ValueError: If token cannot be obtained or validated
    """
```

### **Token Validation Workflow**
```
┌─────────────┐     ┌──────────────┐    ┌─────────────┐
│ Check Env   │  ──▶│ Check Shell  │ ──▶│ Token       │
│ Variable    │     │ Config Files │    │ Found?      │
└─────────────┘     └──────────────┘    └─────────────┘
                                               │
┌─────────────┐     ┌──────────────┐          ▼
│ Guide Token │ ◀───│ Handle       │    ┌─────────────┐
│ Setup       │     │ Expired      │ ◀──│ Validate    │
└─────────────┘     │ Token        │    │ with API    │
      │             └──────────────┘    └─────────────┘
      ▼                     │                  │
┌─────────────┐             │                  ▼
│ Guide Token │             │            ┌─────────────┐
│ Renewal     │ ◀───────────┘            │ Return      │
└─────────────┘                          │ Token +     │
      │                                  │ User Info   │
      ▼                                  └─────────────┘
┌─────────────┐
│ Save New    │
│ Token?      │
└─────────────┘
      │
      ▼
┌─────────────┐
│ Update      │
│ Shell       │
│ Config      │
└─────────────┘
```

## 🔄 Data Flow

### **Workflow Visualization**
```
┌─────────────┐     ┌──────────────┐    ┌─────────────┐     ┌──────────────┐
│ User Input  │  ──▶│ Validation  │ ──▶│ Folder      │ ──▶│ Document     │
│             │     │              │    │ Creation    │     │ Creation     │
└─────────────┘     └──────────────┘    └─────────────┘     └──────────────┘
                                                                     │
┌─────────────┐     ┌──────────────┐    ┌─────────────┐              │
│ Success     │ ◀──│ URL          │ ◀──│ Progress    │ ◀───────────┘
│ Summary     │     │ Generation   │    │ Tracking    │
└─────────────┘     └──────────────┘    └─────────────┘
```
### **Runbook Creation Workflow**
```
User Input → Validation → Folder Creation → Document Creation → Result Display
     ↓            ↓             ↓               ↓               ↓
  Validators → InputValidator → FolderManager → DocumentManager → UserMessenger
```

### **CSV User Addition Workflow**
```
CSV File → Email Extraction → Bulk Resolution → Member Addition → Progress Tracking
    ↓           ↓                  ↓               ↓               ↓
CSVProcessor → CSVUserManager → QuipAPIClient → ProgressBar → UserMessenger
```

## 🚀 Development Environment Setup

### **Local Development**

1. **Clone and setup:**
   ```bash
   git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
   cd CDP-Quip-Runbooker/src/CDP-Quip-Runbooker
   pip install -r requirements.txt
   ```

2. **Set up authentication:**
   ```bash
   export QUIP_API_TOKEN='your-token-here'
   export CDP_DEBUG=true  # Enable debug mode
   ```

3. **Run the refactored version:**
   ```bash
   python cdpRunbooker.py
   ```

### **Virtual Environment Development**

For isolated development with virtual environments:

1. **Setup virtual environment:**
   ```bash
   git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
   cd CDP-Quip-Runbooker/src/CDP-Quip-Runbooker
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install and run:**
   ```bash
   pip install -r requirements.txt
   export QUIP_API_TOKEN='your-token-here'
   python cdpRunbooker.py
   ```

**Example Session:**
```
🎯 CDP Runbook Creation
┌─ Select Runbook Type ─────────────────────────────────────┐
│  1. Core CDP Runbook                                       │  
│  2. Use-case Specific Runbook                             │
└─────────────────────────────────────────────────────────────┘
🔄 Enter your choice: 1

🔄 Enter Customer Name: ACME Corporation
🔄 Enter Engagement Short Name: CloudMigration  
🔄 Enter Engagement Start Month (press Enter for current month 2024-03): 
🔄 Please enter the CDP Engagement SIM ID or press Enter to skip: 493
🔄 Are you creating this for testing purposes? (y/n) [n]: n

▶️ Step 1: Creating core CDP runbook
✅ Created document: CDP_2024-03_ACME-Corporation_CloudMigration_Countdown-Premium-493_Runbook-Core

▶️ Step 2: Creating engagement log  
✅ Created document: CDP_2024-03_ACME-Corporation_CloudMigration_Countdown-Premium-493_Engagement Log

✅ CDP Runbook creation completed successfully!

┌─ Summary ──────────────────────────────────────────────────┐
│ Engagement: CDP_2024-03_ACME-Corporation_CloudMigration_Countdown-Premium-493 │
│ Status: ✓ Successfully Created                              │
│                                                            │
│ 📁 Folder URL:                                            │
│    https://quip-amazon.com/ABC123DEF456                   │
│                                                            │
│ 📄 Document URLs:                                         │
│    • Core Runbook:                                        │
│      https://quip-amazon.com/XYZ789ABC123                 │
│    • Engagement Log:                                      │
│      https://quip-amazon.com/DEF456GHI789                 │
└────────────────────────────────────────────────────────────┘
✅ Your files are ready!
```

## ⚙️ Configuration

### **Environment Variables**

| Variable | Purpose | Example |
|----------|---------|---------|
| `QUIP_API_TOKEN` | Your Quip API token (required) | `export QUIP_API_TOKEN='abc123...'` |
| `CDP_DEBUG` | Enable debug mode | `export CDP_DEBUG=true` |
| `NO_COLOR` | Disable colored output | `export NO_COLOR=1` |

### **Token Management**

The script includes **smart token management**:

1. **Automatic Detection:** Checks for existing tokens in environment and shell config
2. **Guided Setup:** Opens browser and provides multiple secure input methods
3. **Auto-Renewal:** Detects expired tokens and guides renewal process
4. **Secure Storage:** Optionally saves to shell config with proper cleanup

```bash
# Manual token setup
export QUIP_API_TOKEN='your-token-here'

# Permanent setup (adds to ~/.bashrc or ~/.zshrc)
echo "export QUIP_API_TOKEN='your-token-here'" >> ~/.bashrc
source ~/.bashrc
```

### **Folder Naming Convention**

```
CDP_{YYYY-MM}_{CustomerName}_{EngagementName}_{SIM-ID}
```

**Examples:**
- `CDP_2024-03_ACME-Corp_Migration` (without SIM ID)
- `CDP_2024-03_ACME-Corp_Migration_Countdown-Premium-493` (with SIM ID)

---

## 📊 Advanced Features

### **Intelligent Email Resolution**

The system uses a two-phase approach for maximum efficiency:

**Phase 1: Bulk Lookup** (70% of processing time)
```
[████████████████████████████░░░░░░░░░░░░] 70% Phase 1: Bulk email lookup
```
- Processes 1000 emails per API call
- Tries emails exactly as provided
- Uses efficient batch processing

**Phase 2: Domain Fallback** (30% of processing time)  
```
[██████████████████████████████████████] 100% Phase 2: Domain variations
```
- Tries 30+ Amazon domain variations
- Smart username extraction
- Individual fallback processing

### **Rate Limiting Intelligence**

Automatically manages Quip API limits:
- **Monitors** API headers (`X-Ratelimit-Remaining`, `X-Ratelimit-Reset`)
- **Adjusts** timing based on remaining quota  
- **Handles** 429 errors with precise wait times
- **Optimizes** throughput while staying within limits

### **Error Recovery System**

**Automatic Retry Logic:**
- Document creation: 3 attempts with exponential backoff
- API calls: Smart retry based on error type
- Network issues: Progressive delays up to 60 seconds
- Server errors: Cleanup and retry with fresh state

**Graceful Degradation:**
- Partial CSV failures: Process what works, report what doesn't
- Network instability: Reduce batch sizes and increase delays
- Token expiration: Pause workflow, guide renewal, resume

### **Bulk Operations Performance**

| Operation | Batch Size | API Calls | Time (100 users) |
|-----------|------------|-----------|------------------|
| Email Resolution | 1000 users/call | 1 call | ~2 seconds |
| User Addition | 50 users/call | 2 calls | ~5 seconds |
| Domain Fallback | 1 user/call | Variable | ~30 seconds |

### **Advanced CSV Processing**

**Automatic Format Detection:**
```python
# Handles all these formats automatically:
"user1@amazon.com, user2@amazon.com"           # Simple list
"Name,Email\nJohn Doe,john@amazon.com"         # Standard CSV  
"sep=;\nName;Email\nJohn;john@amazon.com"      # Excel format
"username,first_name,email\njdoe,John,john@amazon.com"  # Amazon exports
```

**Smart Domain Resolution:**
- `john@invalid.com` → tries `john@amazon.com`, `john@amazon.co.uk`, etc.
- Covers 30+ Amazon domains worldwide
- Reports original email with resolved domain in results

---

## 🛠️ Administrative Functions

### **Tampermonkey Email Extraction**

For team administrators extracting emails from Amazon's permission system:

1. **Install** the provided `Amazon-Teams-Member-Copier.js` script
2. **Navigate** to your team page: `https://permissions.amazon.com/a/team/*`
3. **Click** "Copy Member Emails" button  
4. **Save** clipboard to CSV file
5. **Run** `python cdpRunbooker.py --add-users team_emails.csv`

### **Bulk Management Commands**

```bash
# Process multiple CSV files
for csv in team_*.csv; do
    python cdpRunbooker.py --add-users "$csv" --folder-id ABC123
done

# Large team processing with progress
python cdpRunbooker.py --add-users large_team.csv --debug
```

---

## 🧪 Testing and Debugging

### **Debug Mode**
```bash
# Enable comprehensive logging
export CDP_DEBUG=true
python cdpRunbooker.py --debug
```

**Debug Output Includes:**
- API request/response details
- Rate limiting status and decisions
- CSV processing step-by-step breakdown
- Token validation and renewal traces
- Progress bar state transitions

### **Manual Testing Checklist**

- [ ] **Token Management**: First-run token setup, renewal, and persistence
  - [ ] First-time Setup: No token present, guided setup workflow
  - [ ] Valid Token: Existing valid token, successful authentication
  - [ ] Expired Token: Expired token detection and renewal workflow
  - [ ] Invalid Token: Malformed token handling
  - [ ] Renewal Process: Complete token renewal and persistent storage
  - [ ] Shell Config: Token saving to appropriate shell configuration files
- [ ] **Folder Creation**: Test vs. production folder placement
- [ ] **Document Creation**: Core and use-case runbooks with proper templates
- [ ] **CSV Processing**: Various formats (simple list, headers, Excel exports)
- [ ] **User Addition**: Bulk operations with progress tracking
- [ ] **Error Handling**: Network failures, rate limits, invalid inputs
- [ ] **UI Components**: Progress bars, colored output, menu navigation

### **Common Development Scenarios**

1. **Testing CSV Operations:**
   ```bash
   # Create test CSV with known users
   echo "user1@amazon.com,user2@amazon.com" > test_users.csv
   python cdpRunbooker.py --add-users test_users.csv --debug
   ```

2. **Testing Document Creation:**
   ```bash
   # Use test folder to avoid cluttering production
   # Script will prompt for test folder preference
   python cdpRunbooker.py
   ```

3. **Performance Testing:**
   ```bash
   # Test with larger CSV files
   python cdpRunbooker.py --add-users large_team.csv --folder-id TEST_FOLDER_ID
   ```

## 🏛️ Code Standards

### **Code Organization**
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Configuration Management**: All constants centralized in `CDPConfig`
- **Error Handling**: Consistent exception handling with user-friendly messages

### **Naming Conventions**
- **Classes**: PascalCase (`DocumentManager`, `CSVUserManager`)
- **Functions**: snake_case (`create_engagement_folder`, `resolve_emails`)
- **Constants**: UPPER_SNAKE_CASE (`CORE_TEMPLATE_ID`, `MAX_RETRIES`)
- **Variables**: snake_case (`folder_id`, `email_to_member_id`)

### **Documentation Standards**
```python
def create_engagement_folder(self, customer_name: str, engagement_name: str, 
                           start_month: str, sim_id: str = "", is_test: bool = False) -> FolderInfo:
    """
    Create a CDP engagement folder with standardized naming.
    
    Args:
        customer_name: Name of the customer for this engagement
        engagement_name: Short descriptive name for the engagement
        start_month: Start month in YYYY-MM format
        sim_id: Optional SIM ID (Countdown-Premium-XXX format)
        is_test: Whether to create in test folder location
        
    Returns:
        FolderInfo object with folder details and URLs
        
    Raises:
        Exception: If folder creation fails
    """
```

### **Error Handling Patterns**
```python
# Comprehensive error handling with user feedback
try:
    result = self.api_operation()
    msg.print_success("Operation completed successfully")
    return result
except QuipAPIError as e:
    msg.print_error(f"API operation failed: {str(e)}")
    if DEBUG_MODE:
        logger.debug(f"API error details: {traceback.format_exc()}")
    raise
except Exception as e:
    msg.print_error(f"Unexpected error: {str(e)}")
    logger.error(f"Unexpected error in operation: {str(e)}")
    raise
```

## 🔄 Rate Limiting Implementation

### **Intelligent Rate Limiting**
The system implements sophisticated rate limiting based on Quip API headers:

```python
def _make_rate_limited_request(self, method, url, **kwargs):
    """Make HTTP request with intelligent rate limiting"""
    # Check current rate limit status
    wait_time = self._should_wait_for_rate_limit()
    if wait_time > 0:
        time.sleep(wait_time)
    
    # Make request and update rate limit info
    response = requests.request(method, url, **kwargs)
    self._update_rate_limit_info(response.headers)
    
    # Handle 429 responses with precise wait times
    if response.status_code == 429:
        reset_time = self.rate_limit_reset or (time.time() + 60)
        wait_time = max(0, reset_time - time.time())
        time.sleep(wait_time + 1)  # Add 1 second buffer
```

### **Batch Processing Strategy**
- **Bulk Operations**: Process 1000 items per API call when possible
- **Conservative Batching**: Use 50-item batches for write operations
- **Progressive Delays**: Increase delays as rate limit approaches
- **Graceful Degradation**: Fall back to smaller batches if needed

## 📊 Performance Considerations

### **Memory Usage**
- **Streaming CSV Processing**: Process large files without loading entirely into memory
- **Lazy Loading**: Load templates and folder data only when needed
- **Cleanup**: Proper cleanup of temporary resources and connections

### **Network Efficiency**
- **Connection Reuse**: Single session for all API calls
- **Compression**: Enable gzip compression for API requests
- **Timeout Management**: Appropriate timeouts to prevent hanging

### **User Experience**
- **Progress Tracking**: Real-time progress for operations > 5 seconds
- **Responsive UI**: Non-blocking operations where possible
- **Clear Feedback**: Immediate acknowledgment of user actions

## 🔒 Security Considerations

### **Token Management**
- **Secure Storage**: Tokens stored in shell configuration files with proper permissions
- **Automatic Cleanup**: Remove old tokens when updating
- **Validation**: Verify token format and permissions before use
- **Renewal Guidance**: User-friendly token renewal process

### **Input Validation**
- **File Path Sanitization**: Prevent directory traversal attacks
- **Email Validation**: Validate email formats before API calls
- **Folder Name Validation**: Sanitize folder names to prevent injection

### **API Security**
- **Request Validation**: Validate all API responses before processing
- **Error Information**: Sanitize error messages to prevent information disclosure
- **Rate Limiting**: Respect API limits to prevent service disruption

## 🚢 Deployment and Maintenance

### **Version Management**
- **Backward Compatibility**: Original script maintained for existing users
- **Migration Path**: Clear upgrade path from original to refactored version
- **Feature Flags**: Ability to enable/disable new features for testing

### **Monitoring and Logging**
- **Comprehensive Logging**: All operations logged with appropriate levels
- **Performance Metrics**: Track operation timing and success rates
- **Error Tracking**: Detailed error logs for troubleshooting

### **Maintenance Tasks**
- **Regular Testing**: Automated testing of core functionality
- **Dependency Updates**: Keep dependencies current with security patches
- **Documentation Updates**: Keep documentation synchronized with code changes

## 🤝 Contributing Guidelines

### **Before Contributing**
1. **Read this guide** thoroughly
2. **Test your changes** with both test and production data
3. **Follow code standards** outlined above
4. **Update documentation** for any new features

### **Pull Request Process**
1. **Feature Branch**: Create a feature branch from mainline
2. **Testing**: Ensure all manual tests pass
3. **Documentation**: Update relevant documentation
4. **Code Review**: Submit for review with clear description

### **Contribution Areas**
- **New Features**: Add new features that make Runbook creation easier for CDP engineers
- **UI Enhancements**: Improve user experience and visual design
- **Performance**: Optimize API usage and processing speed
- **Error Handling**: Enhance error recovery and user guidance
- **Documentation**: Improve guides and troubleshooting information

## 🔍 Troubleshooting Development Issues

### **Common Development Problems**

| Problem | Cause | Solution |
|---------|--------|----------|
| **Import Errors** | Missing dependencies | `pip install -r requirements.txt` |
| **Token Issues** | Invalid/expired token | Run script to renew token |
| **API Errors** | Rate limiting or permissions | Enable debug mode to see details |
| **CSV Processing** | Malformed CSV files | Use debug mode to see parsing details |
| **Module Not Found** | Python path issues | Ensure you're in the correct directory |

### **Debug Information Collection**
```bash
# Collect comprehensive debug information
export CDP_DEBUG=true
python cdpRunbooker.py --debug > debug_output.log 2>&1
```

### **Performance Profiling**
```python
# Add timing to operations
import time
start_time = time.time()
# ... operation ...
logger.debug(f"Operation took {time.time() - start_time:.2f} seconds")
```

---

## 📋 Change History

### Documentation Guidelines

When making changes to CDP Runbooker:
1. **Document changes in this section** under the appropriate version
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Include date, type of change, and key details**
4. **Do NOT create separate documentation files** unless they serve a specific ongoing purpose (like SECURITY.md for user-facing security information)

### Version 2.0.1 (2025-08-12)

#### 🐛 Bug Fixes
- **Authentication: Fixed Redundant Token Validation**
  - **Issue**: Token validation happening twice causing environment-specific failures
    - CDD environments: Token rejected immediately with "invalid or expired" error
    - CDM environments: Token validated initially but failed during QuipAPIClient initialization
  - **Root Cause**: Redundant validation in `QuipAPIClient._validate_token()` after successful validation in `SecureTokenManager`
  - **Solution**: 
    - Removed redundant `_validate_token()` method from QuipAPIClient
    - Modified `QuipAPIClient.__init__()` to use `get_validated_token()` which returns both token and user info
    - Added `_log_initialization_error()` method for enhanced error logging
  - **Impact**: Consistent authentication across all environments (CDD, CDM, etc.)
  - **Files Modified**: `cdpRunbooker.py`

#### ✨ New Features
- **Token Diagnostics Tool**
  - **Purpose**: Diagnose token validation issues with detailed logging
  - **Usage**: `cdpRunbooker --diagnose-token [TOKEN]`
  - **Features**:
    - Network connectivity tests to quip-amazon.com
    - SSL/TLS configuration logging
    - Token format validation
    - Detailed API request/response logging
    - Python version and library compatibility checks
  - **Files Modified**: `core/secure_token_manager.py`, `cdpRunbooker.py`
  - **Key Findings**: 
    - Python 3.12.11 with urllib3 2.5.0 causes token validation failures
    - Python 3.12.9/3.9.19 with urllib3 2.4.0 works correctly
    - **Root Cause Identified**: Missing SSL certificate environment variables in certain environments
    - Required environment variables: `SSL_CERT_FILE` and `SSL_CERT_DIR`
    - Common in CDMs, CDDs, and Python 3.12+ environments
  - **Solution**: Set SSL certificate environment variables:
    ```bash
    export SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
    export SSL_CERT_DIR=/etc/pki/tls/certs
    ```
  - **Alternative Workaround**: Use Python 3.9-3.11 or downgrade urllib3 to 2.4.0

### Version 2.0.0 (2025-07-18)

#### 🔒 Security Enhancement
- **Secure Token Storage Implementation**
  - **Previous Issue**: API tokens stored as plaintext in shell configuration files (`.zshrc`, `.bashrc`)
  - **Solution**: 
    - Implemented encrypted token storage using machine-specific keys
    - Cross-platform support (Windows, Linux, macOS)
    - Automatic migration from legacy storage with cleanup
    - PBKDF2 key derivation with 100,000 iterations + Fernet encryption
  - **Storage Locations**:
    - Linux/macOS: `~/.config/cdp-runbooker/config.json`
    - Windows: `%APPDATA%\cdp-runbooker\config.json`
  - **Files**: Created `core/secure_token_manager.py`, updated authentication flow

#### 🐛 Bug Fixes
- **Import Resolution Issues**
  - **Issue**: `ValueError: attempted relative import beyond top-level package` when running as script
  - **Root Cause**: Relative imports (`from ..utils.user_interface import msg`) failed in direct execution
  - **Solution**: 
    - Created `utils/import_resolver.py` with robust import strategies
    - Added fallback import handling in `core/secure_token_manager.py`
    - Fixed `setup.py` package discovery configuration
  - **Impact**: Script works in all execution contexts (direct, module, installed package)

- **Package Installation Issues**
  - **Issue**: `pip install -e .` failed, requiring `pip3 install -e .`
  - **Solution**: Fixed `setup.py` to explicitly list packages and support Python 3.12
  - **Files**: `setup.py`

#### ✨ New Features
- **Comprehensive Debug Reporting**
  - Added `--debug-report` CLI flag for generating diagnostic reports
  - Created `utils/debug_reporter.py` with system analysis capabilities
  - Automatic debug report generation on critical errors
  - Privacy-safe information sanitization

## 📚 Additional Resources

- **Quip API Documentation**: [https://quip.com/dev/automation/documentation](https://quip.com/dev/automation/documentation)
- **Amazon Internal Quip**: [https://quip-amazon.com/dev/token](https://quip-amazon.com/dev/token)
- **Brazil Python 3**: [https://w.amazon.com/bin/view/BrazilPython3/](https://w.amazon.com/bin/view/BrazilPython3/)
- **Builder Tools**: [https://docs.hub.amazon.dev/builder-toolbox/](https://docs.hub.amazon.dev/builder-toolbox/)

---

*This development guide is maintained alongside the codebase. Please update it when making architectural changes.*
