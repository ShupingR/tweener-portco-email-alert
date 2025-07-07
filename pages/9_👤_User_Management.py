#!/usr/bin/env python3
"""
User Management Page for Tweener Insights
Admin-only page for managing users, roles, and permissions
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_auth import (
    check_authentication, show_login_page, show_user_info, 
    require_permission, user_manager, get_current_user
)

# Page configuration
st.set_page_config(
    page_title="User Management - SummerAI",
    page_icon="👤",
    layout="wide"
)

def main():
    # Check authentication first
    if not check_authentication():
        show_login_page()
        return
    
    # Check admin permission
    require_permission("user_management", "You need administrator privileges to access user management.")
    
    # Show user info in sidebar
    show_user_info()
    
    st.title("👤 User Management")
    st.markdown("**Manage users, roles, and permissions for Tweener Insights**")
    
    # Tabs for different management functions
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "🔑 Roles", "➕ Add User", "📊 Analytics"])
    
    with tab1:
        show_users_tab()
    
    with tab2:
        show_roles_tab()
    
    with tab3:
        show_add_user_tab()
    
    with tab4:
        show_analytics_tab()

def show_users_tab():
    """Display and manage existing users"""
    st.header("Current Users")
    
    users_data = user_manager.get_users()
    users = users_data.get("users", {})
    
    if not users:
        st.warning("No users found.")
        return
    
    # Display users in a table format
    for username, user_data in users.items():
        with st.expander(f"👤 {user_data.get('full_name', username)} ({username})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Username:** {username}  
                **Email:** {user_data.get('email', 'N/A')}  
                **Role:** {user_data.get('role', 'N/A')}  
                **Status:** {'🟢 Active' if user_data.get('active', False) else '🔴 Inactive'}
                """)
            
            with col2:
                st.markdown(f"""
                **Created:** {user_data.get('created_date', 'N/A')[:10] if user_data.get('created_date') else 'N/A'}  
                **Last Login:** {user_data.get('last_login', 'Never')[:10] if user_data.get('last_login') else 'Never'}
                """)
            
            # Action buttons
            col3, col4, col5 = st.columns(3)
            
            with col3:
                if st.button(f"🔄 Reset Password", key=f"reset_{username}"):
                    st.info(f"Password reset functionality for {username} would be implemented here.")
            
            with col4:
                current_status = user_data.get('active', False)
                new_status = not current_status
                status_text = "🔴 Deactivate" if current_status else "🟢 Activate"
                
                if st.button(status_text, key=f"toggle_{username}"):
                    st.info(f"User status toggle for {username} would be implemented here.")
            
            with col5:
                if username != st.session_state.get('username'):  # Don't allow deleting self
                    if st.button(f"🗑️ Delete", key=f"delete_{username}"):
                        st.warning(f"User deletion for {username} would be implemented here.")

def show_roles_tab():
    """Display and manage roles and permissions"""
    st.header("Roles & Permissions")
    
    users_data = user_manager.get_users()
    roles = users_data.get("roles", {})
    
    for role_name, role_data in roles.items():
        with st.expander(f"🔑 {role_name.title()} Role", expanded=False):
            st.markdown(f"**Description:** {role_data.get('description', 'No description')}")
            
            st.markdown("**Permissions:**")
            permissions = role_data.get('permissions', [])
            
            if permissions:
                for perm in permissions:
                    st.markdown(f"- ✅ {perm}")
            else:
                st.markdown("- ❌ No permissions assigned")
            
            # Count users with this role
            user_count = sum(1 for user in users_data.get("users", {}).values() 
                           if user.get("role") == role_name)
            st.markdown(f"**Users with this role:** {user_count}")

def show_add_user_tab():
    """Add new user interface"""
    st.header("Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username*", placeholder="Enter username")
            new_email = st.text_input("Email*", placeholder="user@summerai.biz")
            new_full_name = st.text_input("Full Name*", placeholder="John Doe")
        
        with col2:
            # Get available roles
            users_data = user_manager.get_users()
            available_roles = list(users_data.get("roles", {}).keys())
            new_role = st.selectbox("Role*", available_roles if available_roles else ["viewer"])
            
            new_password = st.text_input("Temporary Password*", type="password", 
                                       placeholder="Enter temporary password")
            new_active = st.checkbox("Active", value=True)
        
        submitted = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if submitted:
            if new_username and new_email and new_full_name and new_password and new_role:
                # Here you would implement the actual user creation
                st.success(f"✅ User {new_username} would be created with role {new_role}")
                st.info("💡 User creation functionality would update the Secret Manager with new user data.")
            else:
                st.error("❌ Please fill in all required fields")

def show_analytics_tab():
    """Show user analytics and statistics"""
    st.header("User Analytics")
    
    users_data = user_manager.get_users()
    users = users_data.get("users", {})
    
    if not users:
        st.warning("No user data available for analytics.")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(users)
        st.metric("Total Users", total_users)
    
    with col2:
        active_users = sum(1 for user in users.values() if user.get('active', False))
        st.metric("Active Users", active_users)
    
    with col3:
        recent_logins = sum(1 for user in users.values() if user.get('last_login'))
        st.metric("Users with Logins", recent_logins)
    
    with col4:
        admin_users = sum(1 for user in users.values() if user.get('role') == 'admin')
        st.metric("Admin Users", admin_users)
    
    # Role distribution
    st.subheader("Role Distribution")
    role_counts = {}
    for user in users.values():
        role = user.get('role', 'unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    if role_counts:
        st.bar_chart(role_counts)
    
    # Recent activity
    st.subheader("Recent User Activity")
    recent_users = []
    for username, user in users.items():
        if user.get('last_login'):
            recent_users.append({
                'Username': username,
                'Full Name': user.get('full_name', 'N/A'),
                'Role': user.get('role', 'N/A'),
                'Last Login': user.get('last_login', 'Never')[:19] if user.get('last_login') else 'Never'
            })
    
    if recent_users:
        # Sort by last login (most recent first)
        recent_users.sort(key=lambda x: x['Last Login'], reverse=True)
        st.dataframe(recent_users, use_container_width=True)
    else:
        st.info("No login activity recorded yet.")

if __name__ == "__main__":
    main()
