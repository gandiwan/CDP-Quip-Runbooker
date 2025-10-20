# Security Enhancement: Secure Token Storage

## Overview

The CDP Runbooker has been updated with a secure, cross-platform token storage system that replaces the previous insecure shell configuration approach.

## Previous Security Issues

**CRITICAL VULNERABILITY (RESOLVED):**
- API tokens were stored as plaintext in shell configuration files (`.zshrc`, `.bashrc`)
- Tokens were visible to anyone with file system access
- Cross-platform compatibility issues on Windows
- Dependency on shell configuration sourcing

## New Security Features

### ✅ **Encrypted Token Storage**
- Tokens are encrypted using machine and user-specific keys
- Uses `cryptography` library with Fernet symmetric encryption
- PBKDF2 key derivation with 100,000 iterations

### ✅ **Cross-Platform Support**
- **Linux/macOS**: `~/.config/cdp-runbooker/config.json`
- **Windows**: `%APPDATA%\cdp-runbooker\config.json`
- Proper file permissions (600) on Unix systems

### ✅ **Automatic Migration**
- Detects insecure tokens in shell configurations
- Prompts user for migration with security warnings
- Automatically removes old plaintext entries
- Clean migration path for existing users

### ✅ **Machine-Specific Encryption**
- Encryption keys derived from:
  - Machine hostname (`platform.node()`)
  - Username (`getpass.getuser()`)
  - Home directory path
- Tokens are non-portable between machines (security feature)

## Migration Process

When you run the CDP Runbooker, it will automatically:

1. **Check for secure token**: Look for encrypted token in config directory
2. **Detect legacy tokens**: Scan shell configs for insecure entries
3. **Prompt for migration**: Show security warning and migration options
4. **Migrate safely**: Encrypt token and remove insecure entries
5. **Clean up**: Remove old shell configuration entries

### Example Migration Flow

```
⚠️  Security Notice: Insecure Token Storage Detected!

We found API tokens stored insecurely in your shell configuration:
  • ~/.zshrc (added by CDP Runbooker)

For better security, we'll migrate to encrypted storage and remove
the insecure entries.

This will:
✓ Move your token to encrypted, cross-platform storage
✓ Remove plaintext tokens from shell configs
✓ Keep your token working in all environments

Continue with migration? (y/n) [y]: y

✅ Migration Complete!
✓ Token encrypted and stored securely
✓ Removed insecure entries from: .zshrc
✓ Your token is now protected and cross-platform compatible

Your CDP Runbooker is ready to use!
```

## Configuration File Format

```json
{
  "version": "1.0",
  "encrypted_token": "gAAAAABh...",
  "created_at": "2025-07-16T21:00:00Z",
  "last_used": "2025-07-16T21:00:00Z",
  "user_name": "John Doe"
}
```

## Security Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Token Storage** | Plaintext in shell configs | Encrypted with machine-specific keys |
| **File Permissions** | Shell config permissions | Restrictive (600) on config file |
| **Cross-Platform** | Unix shell dependent | Works on Linux, macOS, Windows |
| **Environment Variables** | Required shell sourcing | No environment variable dependencies |
| **Migration** | Manual cleanup required | Automatic detection and cleanup |
| **Portability** | Tokens work on any machine | Machine-specific (security feature) |

## Dependencies

The new secure token system requires:

```
cryptography>=3.0.0
```

If the cryptography library is not available, the system falls back to base64 encoding (less secure but better than plaintext).

## Troubleshooting

### Token Not Found
If you get a "token not found" error:
1. Run the script - it will guide you through token setup
2. Visit: https://quip-amazon.com/dev/token
3. Copy your Personal Access Token
4. Paste when prompted

### Migration Issues
If migration fails:
1. The original shell config tokens remain unchanged
2. You can manually run migration again
3. Or set up a new token from scratch

### Config Directory Issues
If the config directory cannot be created:
- **Linux/macOS**: Check permissions on `~/.config/`
- **Windows**: Check permissions on `%APPDATA%/`
- The script will show specific error messages

## For Developers

### Key Generation Algorithm
```python
def _generate_encryption_key(self) -> bytes:
    machine_id = platform.node() or "unknown-machine"
    user_id = getpass.getuser() or "unknown-user" 
    home_path = str(Path.home())
    
    identifier = f"{machine_id}:{user_id}:{home_path}:cdp-runbooker-v1"
    salt = hashlib.sha256(identifier.encode()).digest()[:16]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(identifier.encode()))
    return key
```

### Usage in Code
```python
from core.secure_token_manager import SecureTokenManager

# Get secure token (handles migration automatically)
secure_manager = SecureTokenManager()
token = secure_manager.get_secure_token()

# Store new token securely
success = secure_manager.store_token_securely(new_token)
```

## Security Recommendations

1. **Keep the `cryptography` library updated**
2. **Do not share config files between machines**
3. **Regularly rotate your Quip API tokens**
4. **Report any suspicious token-related activity**
5. **Never commit config files to version control**

## Support

If you encounter any issues with the secure token storage:
1. Check this documentation first
2. Run with `CDP_DEBUG=true` for detailed logging
3. Contact the development team with specific error messages
