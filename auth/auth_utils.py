"""
Authentication utilities for session management
"""

import time
import streamlit as st
from typing import Optional
from .auth_config import is_valid_user, generate_session_token, SESSION_TIMEOUT

def init_auth_session():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def is_session_valid() -> bool:
    """Check if the current session is valid"""
    if not st.session_state.authenticated:
        return False
    
    if not st.session_state.login_time:
        return False
    
    # Check if session has expired
    current_time = time.time()
    if current_time - st.session_state.login_time > SESSION_TIMEOUT:
        logout_user()
        return False
    
    return True

def login_user(username: str, password: str) -> bool:
    """Attempt to log in a user"""
    if is_valid_user(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.session_token = generate_session_token()
        st.session_state.login_time = time.time()
        return True
    return False

def logout_user():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.session_token = None
    st.session_state.login_time = None

def get_current_user() -> Optional[str]:
    """Get the current authenticated username"""
    if is_session_valid():
        return st.session_state.username
    return None

def require_auth():
    """Decorator to require authentication for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_session_valid():
                st.error("Please log in to access this feature.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator 