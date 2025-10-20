# 🚀 CDP Runbooker Support Channel

**Welcome to the CDP Runbooker technical support channel!** This is where CDP engineers can get help with the Runbooker script for creating engagement folders and runbooks.

**🔗 Join the Support Channel:** [#cdp-runbooker-troubleshooting](https://amazon.enterprise.slack.com/archives/C09CGNU5KT6)

## 🎯 **Our Priority**
**Unblock first, troubleshoot later.** If you need a runbook for an active engagement and the script isn't working, let us know immediately. We'll create your engagement folder manually to unblock you, then help troubleshoot when you have time.

## 🔧 **Before Asking for Help**

### 1. **Check Your Environment Setup**
```bash
# 1. Authenticate with Midway
mwinit  # or mwinit -o for CDMs/CDDs

# 2. Look for these SUCCESS indicators in mwinit output:
#    ✓ "Certificates installed successfully"
#    ✓ "Authentication successful" 
#    ✓ No SSL/certificate error messages

# 3. Run script diagnostics
cdpRunbooker --diagnose-token
```

### 2. **Most Common Issues & Quick Fixes**

| **Issue** | **Quick Fix** |
|-----------|---------------|
| **"Authentication failed: 401"** | Token expired → Run `cdpRunbooker` (script will guide renewal) |
| **SSL certificate errors** | Missing cert vars → Add to `.bashrc`/`.zshrc`:<br>`export SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`<br>`export SSL_CERT_DIR=/etc/pki/tls/certs` |
| **"Permission denied on folder"** | Not in CDP team or folder → Use script's CSV function to sync permissions |
| **Import/module errors** | Need reinstall → `cd CDP-Quip-Runbooker && pip install -e .` |
| **Network timeouts** | VPN/connectivity → Check VPN connection |

### 3. **Need Debug Info? Run This:**
```bash
CDP_DEBUG=true cdpRunbooker --debug > debug.log 2>&1
```
**⚠️ IMPORTANT:** Redact any security tokens/keys before sharing output!

## 📝 **When Reporting Issues**

Please include:
1. **Environment:** CDM, CDD, local machine, Python version
2. **Error message:** Exact text (with tokens redacted)
3. **What you tried:** Steps taken before asking
4. **mwinit output:** Any errors from authentication
5. **Diagnostic output:** From `--diagnose-token` if relevant

## 🆘 **Getting Help**

- **🔥 Urgent (blocking active engagement):** Tag the issue as urgent - we'll create your folder manually first
- **🔧 Technical troubleshooting:** Post your debug info in [#cdp-runbooker-troubleshooting](https://amazon.enterprise.slack.com/archives/C09CGNU5KT6)
- **📋 Process questions:** CDP workflows, engagement questions, etc. → Use [#aws-se-countdown-team](https://amazon.enterprise.slack.com/archives/C0648SGJSP6) channel
- **🆘 Escalation:** @fieldinn (only when volunteers can't help)

## 🛠️ **Contributing Fixes**

Found a new issue or fix? Help improve the script:
- **Update documentation:** Submit changes to README.md
- **Code fixes:** Follow DEVELOPMENT.md guidelines  
- **New discoveries:** Share solutions so we can add them to docs

## 🔐 **Deemed Export Access Issues**

### **"lacks citizenship/residency info" Error**

This error occurs when Amazon's Deemed Export compliance requirements haven't been met:

1. **Go to https://atoz.amazon.work/profile**
2. **Select "Manage personal information" → "Work authorization and citizenship"**
3. **Edit "Deemed exports" section and provide your citizenship information**
4. **Wait 2-3 hours for propagation**
5. **For L99 Contingent Workers:** Submit a [SIM ticket](https://t.corp.amazon.com/create/templates/569bd123-ab6b-4878-995a-5d1eedc91262) to the Deemed Export team

### **Package Permission Errors**

Check your specific access: `https://code.amazon.com/packages/CDP-Quip-Runbooker/permissions?user=[your-alias]`

If you're not a member of the required team:
- Contact your manager about joining the aws-countdown-premium team
- Or contact the package owner for access

---

## 🖥️ **Cloud Dev Machine (CDM) and Cloud Dev Desktop (CDD) Setup**

_CDMs and CDDs change frequently. These instructions should be used as rough guides. If you run into issues during setup, ask Q Internal for help: https://ask.qbusiness.aws.dev/#/chat_

### **Cloud Dev Machine (CDM)**
_CDMs are recommended for new CDP Engineers over CDDs because they are simpler and faster to setup. CDMs and CDDs are functionally equivalent for CDP engineers_

#### **Prerequisites**
1. Personal Bindle with valid CTI team association
   * Review your bindle: https://bindles.amazon.com/software_app/[your-alias]'s%20PersonalSoftwareBindle 
   * [Instructions for assigning a CTI to your personal Bindle](https://tiny.amazon.com/r2fsx97r/wamazbinviewBindBindRefeHHoF)
2. Builder Toolbox installed locally
   * Instructions: [Builder Toolbox Getting Started](https://docs.hub.amazon.dev/builder-toolbox/user-guide/getting-started/)
3. AxE CLI installed locally
   ```bash
   toolbox install axe
   ```

#### **Step 1: Create Your CDM**
From your local system:
```bash
mwinit
axe create --region [your-preferred-region] \
           --bindle-id [your-personal-bindle-id] \
            --architecture x86_64 \
            --instance-type c6a.2xlarge \
            --storage-size 500 GB
```
⏱️ Process takes about 15 minutes

#### **Step 2: Connect to CDM**
```bash
axe connect --instance-id [your-instance-id]
```

#### **Step 3: Configure CDM Environment**
```bash
# Generate SSH key
ssh-keygen -t ecdsa

# Setup Midway authentication
mwinit -o --preregister
```
Follow on-screen instructions for security key registration
```bash
# Complete Midway Authentication
mwinit -o

# Setup workspace
wssh setup && chmod 600 ~/.ssh/config && axe init builder-tools
```
Use default options including Python3 installation (~5 mins)
```bash
# Source shell configuration
source ~/.bashrc  # or source ~/.zshrc

# Setup Brazil workspace
brazil setup completion && \
sudo mkdir -p -m 755 /workplace/${USER} && \
sudo chown -R ${USER} /workplace/${USER} && \
ln -s /workplace/${USER} ~/workplace
```

#### **Step 4: Install CDP-Quip-Runbooker on CDM**
Connect to your CDM. From local system:
```bash
# Midway Authenticate
mwinit

# Connect to CDM via SSH or axe
axe connect --instance-id [your-instance-id]
```
From your CDM:
```bash
# Midway Authenticate
mwinit -o

# Create a Brazil workspace
brazil ws create -n WS_CDP-Runbooker

# Change directory
cd WS_CDP-Runbooker

# Pull down the script
brazil ws use -p CDP-Quip-Runbooker -vs CDP-Quip-Runbooker/mainline
 
# Browse to the script
cd src/CDP-Quip-Runbooker

# Run the script:
$bpath/bin/python3 cdpRunbooker.py
```

### **Cloud Dev Desktop (CDD)**
*More details available here: https://guide.aws.dev/articles/AR3htx8hR_QMeZksenqavQ4w Thanks to Tim Pugh (timpug@) for providing these instructions*

#### **Launch Dev Desktop**
1. Visit: https://docs.hub.amazon.dev/dev-setup/clouddesktop-create/
   - If no host appears, switch to a different us-east-1 region
   - For fleet selection, use STP-PS-DevDesktop

#### **Configure Git Access**
1. Follow instructions at: https://w.amazon.com/bin/view/NextGenMidway/UserGuide/OTPSoftwareCertificate
2. Access dev desktop via web terminal: https://builderhub.corp.amazon.com/app.html#cloud-desktop
3. Execute: `mwinit -o --preregister`
4. Navigate to https://midway.amazon.com to confirm certificate (refer to linked instructions for visual guidance)
5. Return to terminal and press Enter to complete registration

#### **Clone Repository**
1. Repository location: https://code.amazon.com/packages/CDP-Quip-Runbooker/trees/mainline#
2. Execute:
   ```bash
   mwinit -o
   git clone ssh://git.amazon.com/pkg/CDP-Quip-Runbooker
   ```
Note: Code requires Python 3.x to run correctly (addressed in next section)

#### **Python Configuration and Developer Tools**
1. Follow setup guide: https://docs.hub.amazon.dev/dev-setup/clouddesktop-configure/#set-up-toolbox
2. Verify toolbox installation: `toolbox --version`
   Note: If already installed, proceed to next step. Otherwise, restart shell session.
3. Install required tools:
   ```bash
   toolbox install axe
   axe init builder-tools
   ```
   - Complete prompts for Python 3.x installation
   - Wait for installation to complete
   - Restart shell session to apply Python version changes

#### **CDP Runbooker Script Execution**
1. Execute:
   ```bash
   mwinit -o
   cd CDP-Quip-Runbooker
   pip install -r requirements.txt
   python cdpRunbooker.py
   ```
2. Follow prompts for:
   - Quip API key setup (automatic process available)
   - Test folder creation
   - Verify success via provided Quip website link

#### **IDE Setup**
1. Local machine requirements:
   - Install VS Code
   - Install extensions: Python, Amazon Q, Remote SSH
2. Configure Amazon Q:
   - Use business license
   - Access via: https://amzn.awsapps.com/start

#### **Remote SSH Configuration**
1. Initial SSH testing:
   - Open terminal (Windows Terminal recommended for Windows OS)
   - Execute: `mwinit -o`
   - Locate dev desktop hostname: https://builderhub.corp.amazon.com/app.html#cloud-desktop
   - Test connection: `ssh <your_alias>@<your_dev_desktop_hostname>`
2. VS Code configuration:
   - Click Remote SSH plugin (blue button, bottom left)
   - Enter hostname with alias (format: alias@hostname)
   - Select "Connect to host"
   - Use file explorer to access dev desktop folders

#### **Final IDE Configuration**
1. Enable required extensions for remote session:
   - Access Extensions tab
   - Enable Python and Amazon Q
   - Configure Amazon Q business version
2. Verify Amazon Q functionality:
   - Open project file (e.g., cdpRunbooker.py)
   - Test Amazon Q with file-specific questions
   - Verify contextual responses

---

## 📚 **Resources**

- **📖 Full Documentation:** [README.md](README.md)
- **🔧 Troubleshooting Guide:** [TOKEN_DIAGNOSTICS.md](TOKEN_DIAGNOSTICS.md)  
- **🌐 Get API Token:** https://quip-amazon.com/dev/token
- **📁 CDP Runbooks Wiki:** https://w.amazon.com/bin/view/AWSSupportPortal/AWSSupportEngineering/Products/Countdown/Runbook/
- **💬 Support Channel:** [#cdp-runbooker-troubleshooting](https://amazon.enterprise.slack.com/archives/C09CGNU5KT6)

---

**ℹ️ This is volunteer-based best-effort support. We're here to help, but response times may vary.**
