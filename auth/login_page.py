"""
Login page component for Tweener Insights Dashboard
"""

import streamlit as st
from .auth_utils import init_auth_session, login_user, is_session_valid, logout_user, get_current_user

def show_login_page():
    """Display the login page"""
    
    # Initialize authentication session
    init_auth_session()
    
    # Check if already authenticated
    if is_session_valid():
        return True
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #4fd1c7, #38b2ac);
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .login-form {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        margin-top: 1rem;
        color: #2d3748;
    }
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Login container
    st.markdown("""
    <div class="login-container">
        <div class="login-title">🔐 Tweener Insights</div>
        <div class="login-subtitle">Portfolio Intelligence Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.container():
        st.markdown("""
        <div class="login-form">
        """, unsafe_allow_html=True)
        
        st.markdown("### Sign In")
        st.markdown("Please enter your credentials to access the dashboard.")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("🔑 Login", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
        
        # Handle login
        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                if login_user(username, password):
                    st.success(f"Welcome, {username}! Redirecting to dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
        
        # Help section
        st.markdown("---")
        st.markdown("**Need help?** Contact your administrator for login credentials.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    return False

def show_logout_section():
    """Show logout section in the sidebar"""
    if is_session_valid():
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {get_current_user()}")
        
        if st.sidebar.button("🚪 Logout"):
            logout_user()
            st.rerun()

def require_authentication():
    """Main authentication wrapper - call this at the start of your main app"""
    # Show login page if not authenticated
    if not show_login_page():
        st.stop()
    
    # Show logout section in sidebar
    show_logout_section() 