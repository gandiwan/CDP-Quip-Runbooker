# CDP Runbook Creator
```
   ╔██████╗██████╗ ██████╗     ██████╗ ██╗   ██╗███╗   ██╗██████╗ ╔██████╗ ╔██████╗ ██╗  ██╗███████╗██████╗ 
   ██╔════╝██╔══██╗██╔══██╗    ██╔══██╗██║   ██║████╗  ██║██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗
   ██║     ██║  ██║██████╔╝    ██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║   ██║██║   ██║█████╔╝ █████╗  ██████╔╝
   ██║     ██║  ██║██╔═══╝     ██╔══██╗██║   ██║██║╚██╗██║██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
   ╚██████╗██████╔╝██║         ██║  ██║╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝╚██████╔╝██║  ██╗███████╗██║  ██║
    ╚═════╝╚═════╝ ╚═╝         ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```
**Streamlining CDP engagements since 2024!**
---

## 🚀 Quick Start (3 Steps)

### **Step 1: Download and Install**
_Follow these instructions. For detailed installation help, see the Installation section below._
```bash
mwinit # or mwinit -o for Cloud Dev Machines (CDMs), Dev Desktops, or Workspaces
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/
pip install -e .
```
### **Step 2: Run the Script **
_The script will help you obtain your Quip API Token. You can now run it from anywhere!_
```bash
cdpRunbooker
```
### **Step 3: Follow the Prompts**
_After getting your API Token, just answer some basic questions._
```
🎯 CDP Runbook Creation
┌─ Select Runbook Type ─────────────────────────────────────┐
│  1. Core CDP Runbook                                      │
│  2. Use-case Specific Runbook                             │
└───────────────────────────────────────────────────────────┘
```

**That's it!** 
_Your CDP engagement folder and runbooks will be created automatically._

> 🔐 **Security Enhancement (v2.0+)**: This version includes secure, encrypted token storage that works across all platforms. API tokens are now encrypted using machine-specific keys and stored in secure configuration directories. The system automatically migrates from insecure shell configuration storage and removes plaintext tokens. See [SECURITY.md](SECURITY.md) for technical details about encryption, migration process, and security features.

---

## 📋 What It Does

CDP Runbook Creator automates the creation of Countdown Premium (CDP) engagement workflows in Quip. It creates organized folder structures, runbook documents, and engagement logs while providing bulk user management capabilities.

### **What Gets Created**

| Item | Description | Example |
|------|-------------|---------|
| **📁 Engagement Folder** | Organized CDP workspace | `CDP_2024-03_ACME-Corp_Migration_Countdown-Premium-493` |
| **📄 Core Runbook** | Main engagement runbook with templates | `{FolderName}_Runbook-Core` |
| **📄 Use-case Runbook** | Specialized runbook (optional) | `{FolderName}_Runbook-Use-case-DataMigration` |
| **📄 Engagement Log** | Timeline and tracking document | `{FolderName}_Engagement Log` |

### **Key Features**

- ✅ **Smart Token Management** - Automatic setup, validation, and renewal with expired token detection
- ✅ **Progress Tracking** - Real-time progress bars `[████████░░] 80%`
- ✅ **Bulk User Operations** - Efficient CSV user addition with domain fallback
- ✅ **Intelligent Rate Limiting** - Respects API limits automatically
- ✅ **Professional UI** - Color-coded messages and consistent formatting
- ✅ **Robust Error Recovery** - Automatic retries and cleanup

---

## 🔧 Installation

### **Quick Installation (Recommended)**

**Prerequisites:** 

#### **🔐 Access Requirements (CRITICAL)**

**⚠️ DEEMED EXPORT COMPLIANCE REQUIRED**
Before you can access the CDP-Quip-Runbooker code repository, you **must** complete Amazon's Deemed Export requirements:

1. **Check your current access:** Try visiting https://code.amazon.com/packages/CDP-Quip-Runbooker
2. **If you see "lacks citizenship/residency info" error:**
   - Go to https://atoz.amazon.work/profile
   - Select "Manage personal information" → "Work authorization and citizenship"  
   - Edit "Deemed exports" section and provide your citizenship information
   - Wait 2-3 hours for propagation, then try accessing the repository again
3. **For L99 Contingent Workers:** If you don't have AtoZ access, submit a [SIM ticket](https://t.corp.amazon.com/create/templates/569bd123-ab6b-4878-995a-5d1eedc91262) to the Deemed Export team

**🔑 FIPS SECURITY KEY REQUIREMENTS**
If you get an error message when attempting to clone the repo saying "You are required by AWS Security to use a FIPS security key for access", then you are currently enrolled in the [digital identity FIPS key enforcement program](https://w.amazon.com/bin/view/AWS_Security_Assurance/Digital_ID). There are two possible reasons:

1. **You are in a [critical permissions group](https://w.amazon.com/bin/view/WWRO_CRM/Engineering/ADMIN/Index/CPG/)** and must use a FIPS key (perhaps you have govcloud access). If so:
   - Ensure your FIPS key is registered at https://register.midway-auth.amazon.com/nextgen
   - Verify it has SSH access enabled

2. **You are not in a [critical permissions group](https://w.amazon.com/bin/view/WWRO_CRM/Engineering/ADMIN/Index/CPG/)** thus this restriction should be removed by the [digital identity team](https://w.amazon.com/bin/view/AWS_Security_Assurance/Digital_ID). If true or you are uncertain if you are in a critical permissions group then [cut a ticket](https://issues.amazon.com/issues/create?template=f470bfa0-da1f-4155-9602-87ad234857fa). Make sure to include the error output from your mwinit attempt like the above example when asking for assistance getting unblocked.

**🌐 NETWORK ACCESS REQUIREMENTS**
If you are on your local work machine and trying to clone the repo, you need either:

1. **Be connected to VPN**, or
2. **Have WSSH installed** - See https://w.amazon.com/bin/view/WSSH/ for installation instructions

#### **✅ Self-Check Your Access**

Before starting, verify you have the required permissions:

1. **Check Deemed Export Status:**
   - Visit: https://code.amazon.com/packages/CDP-Quip-Runbooker
   - If you see any error, follow the Deemed Export steps above

2. **Check Team Membership:**
   - Visit: https://code.amazon.com/packages/CDP-Quip-Runbooker/permissions?user=[your-alias]
   - Replace `[your-alias]` with your Amazon login
   - Verify you're listed as a member of aws-countdown-premium team
   
3. **Check Quip Folder Access:**
   - Try accessing: https://quip-amazon.com/4wX0O30tDBmU/
   - If denied, request access from your manager

#### **📋 Additional Requirements**

1. You must be a member of this Team: https://permissions.amazon.com/a/team/aws-countdown-premium
2. You need access to this Quip folder: https://quip-amazon.com/4wX0O30tDBmU/ (ask your Manager or another engineer)
3. Your system must be running Python 3.7+ 
4. Your system must have access to Amazon internal networks (either VPN or being on-net)
5. Your Yubi key must be registered in Midway (mwinit --preregister, then go to https://register.midway-auth.amazon.com/nextgen/user/show/[your-alias] when directed)

_If your system was NOT setup using instructions from BuilderHub, we recommend you follow the instructions to build a CDM, which can be found in [SUPPORT.md](SUPPORT.md#cloud-dev-machine-cdm-and-cloud-dev-desktop-cdd-setup)._

```bash
# 1. Midway authenticate
mwinit # or mwinit -o for Cloud Dev Machines (CDMs), Dev Desktops, or Workspaces

# 2. Clone repository
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/

# 3. Install globally (secure token setup is automatic)
pip install -e .

# 4. Run from anywhere
cdpRunbooker
```

### **Platform-Specific Installation**

#### **Linux Installation**
```bash
# Authenticate with Midway
mwinit

# Clone repository
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/

# Install globally
pip install -e .

# Run from anywhere
cdpRunbooker
```

#### **macOS Installation**
```bash
# Authenticate with Midway
mwinit

# Clone repository
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/

# Install globally (may need --user flag)
pip install -e . --user

# Run from anywhere
cdpRunbooker
```

#### **Windows Installation**
```powershell
# Authenticate with Midway
mwinit

# Clone repository
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/

# Install globally
pip install -e .

# Run from anywhere
cdpRunbooker
```

### **Virtual Environment Installation (Optional)**

For isolated dependency management:

```bash
# Create virtual environment
python -m venv cdp-runbooker-env

# Activate virtual environment
# Linux/macOS:
source cdp-runbooker-env/bin/activate
# Windows:
# cdp-runbooker-env\Scripts\activate

# Clone and install
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/
pip install -e .

# Run the tool
cdpRunbooker
```

### **Installation Verification**

**Check installation:**
```bash
# Verify package is installed
pip list | grep cdp-runbooker

# Test global command
cdpRunbooker --help

# Test functionality
cdpRunbooker --debug
```

**Expected output:**
```
╔██████╗██████╗ ██████╗     ██████╗ ██╗   ██╗███╗   ██╗██████╗ 
...
CDP Runbooker

options:
  -h, --help            show this help message and exit
  --download DOWNLOAD   Download a Quip doc by thread ID
  --add-users ADD_USERS Add users from CSV
  --folder-id FOLDER_ID Alternate Folder ID
  --debug               Enable debug mode
```

### **Development Installation**

For developers who want to modify the code:

```bash
# Clone repository
git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
cd CDP-Quip-Runbooker/

# Install in development mode
pip install -e .

# Make changes to code...
# Changes are immediately reflected without reinstalling
```

### **Uninstallation**

To remove CDP Runbooker:

```bash
pip uninstall cdp-runbooker
```

### **Installation Troubleshooting**

#### **Common Issues**

**1. "setuptools not found"**
```bash
pip install setuptools wheel
```

**2. "Permission denied" (Linux/macOS)**
```bash
pip install -e . --user
```

**3. "Command not found: cdpRunbooker"**
- Check if pip bin directory is in PATH
- Try: `python -m pip show -f cdp-runbooker`
- Restart terminal/shell

**4. "ModuleNotFoundError"**
- Ensure you're in the correct directory when running `pip install -e .`
- Verify the directory contains `setup.py`

---

## 🔐 Security Features

### **Secure Token Storage**
- **🔒 Encrypted Storage**: Tokens encrypted with machine-specific keys using PBKDF2 + Fernet
- **🖥️ Cross-Platform**: Works on Linux, macOS, and Windows with appropriate file permissions
- **🔄 Automatic Migration**: Detects and migrates insecure shell configuration tokens
- **🧹 Cleanup**: Removes plaintext tokens from shell configs during migration

### **Storage Locations**
- **Linux/macOS**: `~/.config/cdp-runbooker/config.json`
- **Windows**: `%APPDATA%\cdp-runbooker\config.json`
- **Permissions**: Restrictive file permissions (600) on Unix systems

### **Migration Process**
When you run CDP Runbooker, it automatically:
1. Checks for existing secure tokens
2. Detects legacy plaintext tokens in shell configs
3. Prompts for secure migration with clear security warnings
4. Encrypts tokens and removes insecure entries
5. Provides migration status and next steps

For detailed technical information, see [SECURITY.md](SECURITY.md).

---

## 📖 Usage Guide

### **Interactive Mode (Recommended)**

Simply run the command and follow the guided prompts:

```bash
cdpRunbooker
```

### **Command Line Options**

| Command | Purpose | Example |
|---------|---------|---------|
| `cdpRunbooker` | Interactive runbook creation | Creates folder + runbooks |
| `cdpRunbooker --add-users CSV_FILE` | Add users from CSV to CDP folder | `cdpRunbooker --add-users team_members.csv` |
| `cdpRunbooker --download THREAD_ID` | Download Quip document as HTML | `cdpRunbooker --download ABC123DEF456` |
| `cdpRunbooker --folder-id FOLDER_ID` | Override default folder for CSV ops | `cdpRunbooker --folder-id XYZ789ABC123` |
| `cdpRunbooker --debug` | Enable verbose logging | Shows detailed progress |

### **CSV User Addition**

Add multiple users to CDP folders efficiently:

```bash
cdpRunbooker --add-users team_members.csv
```

**Progress Display:**
```
▶️ Step 3: Bulk resolving emails to member IDs
[████████████████████████████████████████] 100% Resolving emails

📊 User Addition Summary
  📄 Total emails in CSV: 150
  ✅ Successfully resolved: 145  
  ⚠️ Already members (skipped): 12
  ❌ Failed to resolve: 5
  ➕ Successfully added: 133
```

**Supported CSV Formats:**
- **Simple List:** `user1@amazon.com, user2@amazon.com, user3@amazon.com`
- **With Headers:** `Name,Email,Department` with data rows
- **Amazon Exports:** Employee data with username/email columns
- **Excel Format:** Automatically handles `sep=` directives

---

## 🔄 After Pulling Updates

### **IMPORTANT: Always Reinstall After Git Pull**

When you pull updates from the repository, **always** run the installation command again:

```bash
cd CDP-Quip-Runbooker/
pip install -e .
```

### **Why This Matters**

New features often require additional Python packages that get added to `requirements.txt`. If you don't reinstall, you'll see errors like:

```
❌ No module named 'idna'
❌ No module named 'certifi' 
❌ ImportError: cannot import name 'something' from 'requests'
```

### **Automatic Detection**

Starting with version 2.0+, the script automatically:
- ✅ Detects missing dependencies at startup
- ✅ Provides clear error messages with installation instructions  
- ✅ Warns when your installation might be out of date
- ✅ Guides you through the fix process

### **Best Practice Workflow**

```bash
# 1. Pull latest changes
git pull

# 2. ALWAYS reinstall (takes ~30 seconds)
pip install -e .

# 3. Run the script
cdpRunbooker
```

This prevents **95% of common user issues** and ensures you have the latest features and fixes.

---

## 🆘 Troubleshooting

### **Quick Diagnostic Commands**

```bash
# Check authentication
cdpRunbooker --debug

# Test with minimal CSV
echo "user1@amazon.com,user2@amazon.com" > test.csv
cdpRunbooker --add-users test.csv

# Enable comprehensive logging  
export CDP_DEBUG=true
cdpRunbooker > debug.log 2>&1
```

### **Common Issues & Solutions**

| 🔴 Problem | 💡 Solution |
|------------|-------------|
| **"No module named 'idna'" or other import errors** | **MOST COMMON:** You pulled updates but didn't reinstall dependencies.<br>**Quick Fix:** `cd CDP-Quip-Runbooker && pip install -e .`<br>**Always run this after git pull!** |
| **"lacks citizenship/residency info" during git clone** | **Deemed Export requirement not met**<br>1. Go to https://atoz.amazon.work/profile<br>2. Select "Work authorization and citizenship"<br>3. Edit "Deemed exports" section and provide citizenship info<br>4. Wait 2-3 hours, then try again<br>5. L99 workers: Use [SIM ticket](https://t.corp.amazon.com/create/templates/569bd123-ab6b-4878-995a-5d1eedc91262) |
| **"Permission denied" on package access** | **Check permissions:** https://code.amazon.com/packages/CDP-Quip-Runbooker/permissions?user=[your-alias]<br>Contact package owner if not a team member |
| **"QUIP_API_TOKEN not set"** | Run script - it will guide you through token setup |
| **"Authentication failed: 401 Invalid access_token"** | Token expired - script will automatically detect and guide renewal |
| **"Failed to create folder: 401 Invalid access_token"** | Token validation failed - follow prompts to get new token |
| **"Authentication failed"** | Token expired - script will help you get a new one |
| **"Permission denied on folder"** | Verify access to [CDP Engagements folder](https://quip-amazon.com/4wX0O30tDBmU) |
| **"No emails found in CSV"** | Check file format - try simple comma-separated list |
| **"Rate limit exceeded"** | Script handles this automatically - just wait |
| **"Network timeout"** | Check VPN connection and retry |
| **"Token validation fails with SSL/TLS errors"** | Missing SSL certificate environment variables. Check with: `env \| grep -i ssl`<br>Should show:<br>`SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`<br>`SSL_CERT_DIR=/etc/pki/tls/certs`<br>If missing, add to your shell profile (`.bashrc`, `.zshrc`) |
| **"SSL: CERTIFICATE_VERIFY_FAILED error"** | Check your certificates. See [this article for details](https://w.amazon.com/bin/view/Chime/Engineering/Media/StandardDevelopmentSetup/) |
| **"SSL certificate verification errors"** | The script automatically configures SSL certificates using `certifi`. If you still see SSL errors, you can manually set: `export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")` | 
| **"The read operation timed out error"** | Try running the script again. If it still fails, open a ticket [here](https://t.corp.amazon.com/create/templates/ea8228e6-1088-4b77-8e18-91a042a40bb1) |

### **Troubleshooting Decision Tree**

```
❓ Having Issues?
│
├── 🔐 Authentication Problems?
│   ├── Token missing? ──▶ Run script, it will guide setup
│   ├── Token expired? ──▶ Script detects and helps renew  
│   └── Permission denied? ──▶ Check folder access rights
|
├── 🌐 Network Issues?
│   ├── Timeouts? ──▶ Check VPN connection
│   ├── Rate limits? ──▶ Script handles automatically
│   └── API errors? ──▶ Enable --debug for details
│
├── 📄 CSV Problems?
│   ├── No emails found? ──▶ Try simple format: email1,email2,email3
│   ├── Format errors? ──▶ Use --debug to see parsing details
│   └── Large files slow? ──▶ Normal - progress bars show status
│
└── 🐛 Other Issues?
    ├── Enable debug: export CDP_DEBUG=true
    ├── Check logs for specific error messages
    └── Try with minimal test data first
```

### **Debug Information**

**Enable debug mode for detailed diagnostics:**
```bash
export CDP_DEBUG=true
cdpRunbooker --debug
```

**Debug output includes:**
- API request/response details
- Rate limiting status and decisions  
- CSV processing step-by-step breakdown
- Token validation and renewal traces
- Progress bar state transitions
- Network timing and retry logic

### **FAQ**

**Q: Can I undo folder/document creation?**
A: Yes, you can delete the created folder and documents manually in Quip. The script doesn't provide an undo feature.

**Q: What if the script gets interrupted?**
A: It's safe to re-run. The script will detect existing folders/documents and avoid duplicates. You may have to clean up a folder that was interrupted during creation. 

**Q: Can I create multiple engagements at once?**
A: No, each engagement should be created separately to ensure proper organization and tracking.

**Q: How do I find the folder ID for CSV operations?**
A: The folder ID is in the URL: `https://quip-amazon.com/ABC123DEF456` → `ABC123DEF456`

**Q: How do I add users to an existing CDP folder?**
A: Use `--add-users your_file.csv --folder-id FOLDER_ID` where FOLDER_ID is from the folder URL.

---

## 🔗 Resources

- **📖 Development Guide:** See `DEVELOPMENT.md` for technical details and change history
- **🌐 Quip API Token:** [https://quip-amazon.com/dev/token](https://quip-amazon.com/dev/token)
- **📁 CDP Engagements Folder:** [Active CDP Engagements](https://quip-amazon.com/4wX0O30tDBmU)
- **🔧 Builder Tools:** [Builder Toolbox Documentation](https://docs.hub.amazon.dev/builder-toolbox/)

**✨ Made with ❤️ by the Product Operations TPM team, who are passionate about streamlining CDP engagements!**

---

## 🆘 Need Help?

- **📖 For detailed troubleshooting and CDM/CDD setup guides:** See [SUPPORT.md](SUPPORT.md)
- **💬 Chat support:** [#cdp-runbooker-troubleshooting](https://amazon.enterprise.slack.com/archives/C09CGNU5KT6)
- **🔐 Deemed Export issues:** [Detailed steps in SUPPORT.md](SUPPORT.md#deemed-export-access-issues)
