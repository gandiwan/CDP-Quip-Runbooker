# CDP Runbooker Token Diagnostics

This tool helps diagnose authentication issues with the CDP Runbooker, particularly for environment-specific token validation failures.

## Quick Start

### Run Token Diagnostics

1. **Test stored token:**
   ```bash
   python cdpRunbooker.py --diagnose-token
   ```

2. **Test a specific token:**
   ```bash
   python cdpRunbooker.py --diagnose-token "YOUR_TOKEN_HERE"
   ```

3. **Enable debug mode for more details:**
   ```bash
   CDP_DEBUG=true python cdpRunbooker.py --diagnose-token
   ```

## What the Diagnostics Check

### Test 1: Network Connectivity
- DNS resolution for platform.quip-amazon.com
- Essential for API communication

### Test 2: HTTPS Connectivity
- Verifies HTTPS connection to Quip servers
- Checks for firewall/proxy issues

### Test 3: Token Format
- Validates token length and structure
- Checks for common format patterns

### Test 4: API Validation
- Python version and SSL information
- Library versions (requests, urllib3)
- Certificate paths and validation
- Direct API request with full response details
- Enhanced error logging for SSL/certificate issues

## Common Issues and Solutions

### SSL Certificate Environment Variables
**Most Common Issue**: Missing SSL certificate environment variables
- **Check your environment**: `env | grep -i ssl`
- **Should show**:
  ```
  SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
  SSL_CERT_DIR=/etc/pki/tls/certs
  ```
- **If missing**: Add to your shell profile (`.bashrc`, `.zshrc`):
  ```bash
  export SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
  export SSL_CERT_DIR=/etc/pki/tls/certs
  ```
- **Common in**: CDMs, CDDs, and certain Python 3.12+ environments

### Python 3.12 Compatibility
If you're using Python 3.12 and experiencing issues:
- The diagnostics will show SSL version differences
- May need to update certificate bundles
- Consider using Python 3.9-3.11 if issues persist

### Token Format Issues
Valid tokens typically:
- Have 3 parts separated by `|`
- Are at least 30 characters long
- Example: `BASE64PART|TIMESTAMP|HASHPART`

### SSL/Certificate Errors
The diagnostics will show:
- SSL version being used
- Certificate validation details
- Full error traceback for SSL issues

## Example Output

```
=== CDP Runbooker Token Diagnostics ===

Test 1: Network connectivity to quip-amazon.com
✓ DNS resolution successful

Test 2: HTTPS connectivity
✓ HTTPS connection successful (status: 200)

Test 3: Token format check
✓ Token format appears valid (3 parts, total length: 95)

Test 4: Token validation with API
Python Version: 3.12.11
SSL Version: OpenSSL 3.0.2 15 Mar 2022
Requests Version: 2.32.4
urllib3 Version: 2.5.0
Certifi CA Bundle: /path/to/certifi/cacert.pem
Using amazoncerts module for SSL
API Base URL: https://platform.quip-amazon.com
Token Format: QkxPOU1BMkV1a3g=|178...0= (length: 95)
Making API request to validate token...
Direct API URL: https://platform.quip-amazon.com/1/users/current
Request Headers: Authorization: Bearer [REDACTED]
Response Status: 401
Response Headers: {'Content-Type': 'application/json', ...}
API Error Response: {"error": "invalid_token", "error_description": "Token is invalid or expired"}
Direct API request failed: HTTP 401
Authentication error - token appears to be invalid or expired

✗ Token validation FAILED

Possible causes:
1. Token has expired - get a new one from https://quip-amazon.com/dev/token
2. Token was copied incorrectly - ensure no extra spaces or characters
3. Network/firewall issues - check VPN connection if working remotely
4. SSL/certificate issues - may need to update certificates
```

## Next Steps

1. **If token is expired:** Get a new token from https://quip-amazon.com/dev/token
2. **If Python version issue:** Consider using Python 3.9-3.11
3. **If SSL issues:** Update certificates or check with IT
4. **Share diagnostics:** When reporting issues, include the full diagnostic output

## Generate Full Debug Report

For comprehensive system information:
```bash
python cdpRunbooker.py --debug-report
```

This creates a detailed report including:
- System information
- Python environment
- Import analysis
- File structure validation
- Dependency versions
