#!/usr/bin/env python3
"""
Enhanced User Authentication Module for Tweener Insights
Supports multiple users with different access levels and integrates with Google Cloud IAM
"""

import streamlit as st
import hashlib
import os
import json
from datetime import datetime, timedelta
import logging

# Try to import Google Cloud Secret Manager, fallback to local if not available
try:
    from google.cloud import secretmanager
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    secretmanager = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress Google Cloud warnings for local development
if not GOOGLE_CLOUD_AVAILABLE:
    logging.getLogger('google').setLevel(logging.ERROR)
    logging.getLogger('google.cloud').setLevel(logging.ERROR)
    logging.getLogger('google.auth').setLevel(logging.ERROR)

class UserManager:
    def __init__(self):
        self.project_id = "famous-rhythm-465100-p6"
        self.users_secret_name = "USER_CREDENTIALS"
        self.session_timeout = 8 * 60 * 60  # 8 hours in seconds
        
    def get_secret(self, secret_name):
        """Retrieve secret from Google Cloud Secret Manager or local fallback"""
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                # Only log the warning once per session for credentials
                if not hasattr(self, '_gcp_warning_shown'):
                    logger.info(f"Using local fallback (GCP not available): {e}")
                    self._gcp_warning_shown = True
        
        # Fallback to local file or environment variable for local development
        return self._get_local_secret(secret_name)
    
    def _get_local_secret(self, secret_name):
        """Get secret from local file or environment variable"""
        # Try local users file first
        local_users_file = "local_users.json"
        if secret_name == self.users_secret_name and os.path.exists(local_users_file):
            try:
                with open(local_users_file, 'r') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read local users file: {e}")
        
        # Try environment variable
        env_value = os.getenv(secret_name, "")
        if env_value:
            return env_value
        
        # Return default users for USER_CREDENTIALS if nothing else works
        if secret_name == self.users_secret_name:
            return self._get_default_users_json()
        
        return ""
    
    def _get_default_users_json(self):
        """Return default users as JSON string"""
        default_users = {
            "users": {
                "admin": {
                    "password_hash": self.hash_password("TweenerAdmin2025"),
                    "role": "admin",
                    "full_name": "Portfolio Admin",
                    "created_date": datetime.now().isoformat(),
                    "last_login": None,
                    "active": True
                },
                "viewer": {
                    "password_hash": self.hash_password("ViewerAccess2025"),
                    "role": "viewer",
                    "full_name": "Portfolio Viewer",
                    "created_date": datetime.now().isoformat(),
                    "last_login": None,
                    "active": True
                },
                "analyst": {
                    "password_hash": self.hash_password("AnalystAccess2025"),
                    "role": "analyst", 
                    "full_name": "Portfolio Analyst",
                    "created_date": datetime.now().isoformat(),
                    "last_login": None,
                    "active": True
                }
            },
            "roles": {
                "admin": {
                    "permissions": ["read", "write", "delete", "user_management", "settings"],
                    "description": "Full access to all features"
                },
                "viewer": {
                    "permissions": ["read"],
                    "description": "Read-only access to dashboard"
                },
                "analyst": {
                    "permissions": ["read", "write"],
                    "description": "Can view and create reports"
                }
            }
        }
        return json.dumps(default_users, indent=2)

    def create_user_credentials_secret(self):
        """Create initial user credentials in Secret Manager or local file"""
        if not GOOGLE_CLOUD_AVAILABLE:
            # Create local users file for development
            local_users_file = "local_users.json"
            users_json = self._get_default_users_json()
            try:
                with open(local_users_file, 'w') as f:
                    f.write(users_json)
                logger.info("Created local users file for development")
                return
            except Exception as e:
                logger.error(f"Failed to create local users file: {e}")
                return
        
        try:
            client = secretmanager.SecretManagerServiceClient()
            
            # Default users configuration
            default_users = {
                "users": {
                    "admin": {
                        "password_hash": self.hash_password("TweenerAdmin2025"),
                        "role": "admin",
                        "full_name": "Portfolio Admin",
                        "created_date": datetime.now().isoformat(),
                        "last_login": None,
                        "active": True
                    },
                    "viewer": {
                        "password_hash": self.hash_password("ViewerAccess2025"),
                        "role": "viewer",
                        "full_name": "Portfolio Viewer",
                        "created_date": datetime.now().isoformat(),
                        "last_login": None,
                        "active": True
                    }
                },
                "roles": {
                    "admin": {
                        "permissions": ["read", "write", "delete", "user_management", "settings"],
                        "description": "Full access to all features"
                    },
                    "viewer": {
                        "permissions": ["read"],
                        "description": "Read-only access to dashboard"
                    },
                    "analyst": {
                        "permissions": ["read", "write"],
                        "description": "Can view and create reports"
                    }
                }
            }
            
            # Convert to JSON
            users_json = json.dumps(default_users, indent=2)
            
            # Try to create the secret
            try:
                secret_path = f"projects/{self.project_id}/secrets/{self.users_secret_name}"
                client.create_secret(
                    request={
                        "parent": f"projects/{self.project_id}",
                        "secret_id": self.users_secret_name,
                        "secret": {"replication": {"automatic": {}}}
                    }
                )
                logger.info(f"Created secret {self.users_secret_name}")
            except Exception as e:
                logger.info(f"Secret {self.users_secret_name} already exists or error: {e}")
            
            # Add the initial version
            client.add_secret_version(
                request={
                    "parent": f"projects/{self.project_id}/secrets/{self.users_secret_name}",
                    "payload": {"data": users_json.encode("UTF-8")}
                }
            )
            logger.info("User credentials initialized in Secret Manager")
            
        except Exception as e:
            logger.error(f"Failed to create user credentials secret: {e}")

    def get_users(self):
        """Get all users from Secret Manager"""
        try:
            users_json = self.get_secret(self.users_secret_name)
            if users_json:
                return json.loads(users_json)
            else:
                # Initialize if doesn't exist
                self.create_user_credentials_secret()
                users_json = self.get_secret(self.users_secret_name)
                return json.loads(users_json) if users_json else {"users": {}, "roles": {}}
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return {"users": {}, "roles": {}}

    def hash_password(self, password):
        """Hash password with salt"""
        salt = "summerai_dashboard_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def verify_password(self, username, password):
        """Verify user password"""
        users_data = self.get_users()
        user = users_data.get("users", {}).get(username)
        
        if not user or not user.get("active", False):
            return False
            
        password_hash = self.hash_password(password)
        return user.get("password_hash") == password_hash

    def get_user_info(self, username):
        """Get user information"""
        users_data = self.get_users()
        return users_data.get("users", {}).get(username)

    def update_last_login(self, username):
        """Update user's last login time"""
        try:
            users_data = self.get_users()
            if username in users_data.get("users", {}):
                users_data["users"][username]["last_login"] = datetime.now().isoformat()
                
                if GOOGLE_CLOUD_AVAILABLE:
                    # Update secret in Google Cloud
                    client = secretmanager.SecretManagerServiceClient()
                    users_json = json.dumps(users_data, indent=2)
                    client.add_secret_version(
                        request={
                            "parent": f"projects/{self.project_id}/secrets/{self.users_secret_name}",
                            "payload": {"data": users_json.encode("UTF-8")}
                        }
                    )
                else:
                    # Update local file
                    local_users_file = "local_users.json"
                    users_json = json.dumps(users_data, indent=2)
                    with open(local_users_file, 'w') as f:
                        f.write(users_json)
        except Exception as e:
            logger.error(f"Failed to update last login for {username}: {e}")

    def check_permission(self, username, permission):
        """Check if user has specific permission"""
        user = self.get_user_info(username)
        if not user:
            return False
            
        role = user.get("role")
        users_data = self.get_users()
        role_permissions = users_data.get("roles", {}).get(role, {}).get("permissions", [])
        
        return permission in role_permissions

# Global user manager instance
user_manager = UserManager()

def show_login_page():
    """Display the login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-header {
        text-align: center;
        color: #4fd1c7;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="login-header">🔐 Tweener Insights</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Please log in to access your portfolio dashboard</p>', unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submitted:
            if username and password:
                if user_manager.verify_password(username, password):
                    # Successful login
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now()
                    
                    # Update last login
                    user_manager.update_last_login(username)
                    
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Help section
    st.markdown("---")
    st.markdown("""
    ### 🔒 Security Features
    - Secure password hashing
    - Session management with timeout
    - Role-based access control
    - Integration with Google Cloud IAM
    
    ### 💡 Need Help?
    Contact your administrator for account access or password reset.
    """)

def check_authentication():
    """Check if user is authenticated and session is valid"""
    if not st.session_state.get("authenticated", False):
        return False
    
    # Check session timeout
    login_time = st.session_state.get("login_time")
    if login_time:
        session_duration = datetime.now() - login_time
        if session_duration.total_seconds() > user_manager.session_timeout:
            # Session expired
            st.session_state.clear()
            st.warning("⏰ Your session has expired. Please log in again.")
            return False
    
    return True

def get_current_user():
    """Get current logged-in user information"""
    username = st.session_state.get("username")
    if username:
        return user_manager.get_user_info(username)
    return None

def check_permission(permission):
    """Check if current user has specific permission"""
    username = st.session_state.get("username")
    if username:
        return user_manager.check_permission(username, permission)
    return False

def show_user_info():
    """Show current user info in sidebar"""
    user = get_current_user()
    if user:
        st.sidebar.markdown("### 👤 User Info")
        st.sidebar.info(f"**{user.get('full_name', 'Unknown')}**\n\nRole: {user.get('role', 'N/A').title()}\nEmail: {user.get('email', 'N/A')}")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

def require_permission(permission, message="You don't have permission to access this feature."):
    """Decorator/function to require specific permission"""
    if not check_permission(permission):
        st.error(f"🔒 {message}")
        st.stop()

# Initialize user system on import
if __name__ != "__main__":
    try:
        # Initialize user credentials if they don't exist
        users_data = user_manager.get_users()
        if not users_data.get("users"):
            user_manager.create_user_credentials_secret()
    except Exception as e:
        logger.error(f"Failed to initialize user system: {e}")
