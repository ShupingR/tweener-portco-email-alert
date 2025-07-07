#!/usr/bin/env python3
"""
Simple authentication module for Streamlit app
"""

import streamlit as st
import hashlib
import os
from google.cloud import secretmanager

def get_secret(secret_name):
    """Retrieve secret from Google Cloud Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = "famous-rhythm-465100-p6"
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        # Fallback to environment variable for local development
        return os.getenv(secret_name, "")

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Returns True if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        admin_password = get_secret("ADMIN_PASSWORD")
        if st.session_state["password"] == admin_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.markdown("### 🔐 SummerAI Email Dashboard Login")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Enter your admin password to access the dashboard"
        )
        st.markdown("---")
        st.info("💡 This is your secure SummerAI email alert dashboard. Please enter your credentials to continue.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.markdown("### 🔐 SummerAI Email Dashboard Login")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Enter your admin password to access the dashboard"
        )
        st.error("😞 Password incorrect. Please try again.")
        return False
    else:
        # Password correct
        return True

def logout():
    """Logout function to clear session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def show_auth_status():
    """Show authentication status in sidebar"""
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        st.sidebar.success("🔓 Authenticated as Admin")
        if st.sidebar.button("🚪 Logout"):
            logout()
        return True
    return False
