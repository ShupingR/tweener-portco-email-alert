"""
Authentication configuration for Tweener Insights Dashboard
"""

import os
import hashlib
import secrets
from typing import Dict, Optional

# Default admin credentials (change these!)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "TweenerAdmin2025"  # Production credential

# Additional users (username: password)
ADDITIONAL_USERS = {
    "viewer": "ViewerAccess2025",
    "analyst": "AnalystAccess2025"
}

# Session timeout (in seconds) - 8 hours
SESSION_TIMEOUT = 8 * 60 * 60

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def get_all_users() -> Dict[str, str]:
    """Get all users with their hashed passwords"""
    users = {
        DEFAULT_ADMIN_USERNAME: hash_password(DEFAULT_ADMIN_PASSWORD),
        **{username: hash_password(password) for username, password in ADDITIONAL_USERS.items()}
    }
    return users

def is_valid_user(username: str, password: str) -> bool:
    """Check if username and password are valid"""
    # First check users.json file
    try:
        import json
        users_file = os.path.join(os.path.dirname(__file__), "users.json")
        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                file_users = json.load(f)
                if username in file_users:
                    return verify_password(password, file_users[username])
    except Exception:
        pass
    
    # Fall back to hardcoded users
    users = get_all_users()
    if username not in users:
        return False
    return verify_password(password, users[username])

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

# Environment variable overrides (for production)
def get_admin_username() -> str:
    """Get admin username from environment or default"""
    return os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)

def get_admin_password() -> str:
    """Get admin password from environment or default"""
    return os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD) 