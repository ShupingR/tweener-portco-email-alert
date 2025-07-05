# 🔐 Security Guide - Tweener Insights Dashboard

## Overview
This guide covers the authentication and security features implemented in the Tweener Insights Dashboard.

## Authentication System

### Features
- **Session-based authentication** with automatic timeout (8 hours)
- **Password hashing** using SHA-256
- **Multiple user support** with individual credentials
- **Secure session tokens** for session management
- **Environment variable support** for production deployments

### Default Credentials
⚠️ **IMPORTANT**: Change these default credentials immediately!

- **Admin**: `admin` / `tweener2024`
- **Scot**: `scot` / `tweener_scot_2024`
- **Nikita**: `nikita` / `tweener_nikita_2024`
- **Shuping**: `shuping` / `tweener_shuping_2024`

## User Management

### Adding Users
```bash
python manage_users.py add <username> <password>
```

### Removing Users
```bash
python manage_users.py remove <username>
```

### Changing Passwords
```bash
python manage_users.py change <username> <new_password>
```

### Listing Users
```bash
python manage_users.py list
```

## Security Best Practices

### 1. Change Default Passwords
Immediately change all default passwords after installation:
```bash
python manage_users.py change admin <new_secure_password>
python manage_users.py change scot <new_secure_password>
python manage_users.py change nikita <new_secure_password>
python manage_users.py change shuping <new_secure_password>
```

### 2. Use Strong Passwords
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, and symbols
- Avoid common words or patterns
- Use unique passwords for each user

### 3. Environment Variables (Production)
For production deployments, use environment variables:
```bash
export ADMIN_USERNAME=your_admin_username
export ADMIN_PASSWORD=your_secure_admin_password
```

### 4. HTTPS in Production
Always use HTTPS in production environments:
- Configure SSL certificates
- Set `ENABLE_HTTPS=true` in environment variables
- Use secure headers

### 5. Regular Security Updates
- Update dependencies regularly
- Monitor for security vulnerabilities
- Rotate passwords periodically

## File Security

### Protected Files
- `auth_config.py` - Contains authentication logic
- `users.json` - Contains hashed passwords (if using file-based storage)
- `.env` - Contains sensitive environment variables

### File Permissions
Ensure sensitive files have restricted permissions:
```bash
chmod 600 auth_config.py
chmod 600 users.json
chmod 600 .env
```

## Session Management

### Session Timeout
- Default: 8 hours (28800 seconds)
- Configurable via `SESSION_TIMEOUT` environment variable
- Automatic logout on timeout

### Session Security
- Secure session tokens generated using `secrets.token_urlsafe()`
- Session state managed in Streamlit session state
- Automatic cleanup on logout

## Deployment Security

### Local Development
- Use strong passwords even in development
- Don't commit credentials to version control
- Use `.env` files for local configuration

### Production Deployment
- Use environment variables for all credentials
- Enable HTTPS
- Configure proper firewall rules
- Regular security audits
- Monitor access logs

## Troubleshooting

### Common Issues
1. **Login not working**: Check username/password, ensure no extra spaces
2. **Session timeout**: Sessions expire after 8 hours, re-login required
3. **Permission errors**: Check file permissions on sensitive files

### Security Incidents
If you suspect a security breach:
1. Immediately change all passwords
2. Review access logs
3. Check for unauthorized access
4. Consider rotating session tokens
5. Update security configurations

## Compliance Notes

### Data Protection
- All passwords are hashed using SHA-256
- No plaintext passwords stored
- Session data is temporary and cleared on logout

### Access Control
- Authentication required for all dashboard access
- Individual user accounts with unique credentials
- Session-based access control

## Support
For security-related issues or questions, contact your system administrator. 