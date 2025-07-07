"""
Authentication package for Tweener Insights Dashboard
"""

# Import from user_auth.py (main authentication module)
from .user_auth import (
    check_authentication, 
    show_login_page, 
    show_user_info, 
    get_current_user, 
    check_permission,
    require_permission,
    user_manager
)

# Import from other auth modules (legacy support)
from .auth_config import is_valid_user, get_all_users, hash_password, verify_password
from .auth_utils import init_auth_session, is_session_valid, login_user, logout_user
from .login_page import show_logout_section, require_authentication

__all__ = [
    # Main authentication functions
    'check_authentication',
    'show_login_page', 
    'show_user_info',
    'get_current_user',
    'check_permission',
    'require_permission',
    'user_manager',
    
    # Legacy functions (for backward compatibility)
    'is_valid_user',
    'get_all_users', 
    'hash_password',
    'verify_password',
    'init_auth_session',
    'is_session_valid',
    'login_user',
    'logout_user',
    'show_logout_section',
    'require_authentication'
] 