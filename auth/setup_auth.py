#!/usr/bin/env python3
"""
Authentication Setup Script for Tweener Insights Dashboard
"""

import os
import sys
import getpass

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import auth_config directly since this is a standalone script
import sys
import os
sys.path.append(os.path.dirname(__file__))
from auth_config import hash_password, get_all_users

def setup_initial_auth():
    """Interactive setup for initial authentication configuration"""
    print("🔐 Tweener Insights - Authentication Setup")
    print("=" * 50)
    print()
    
    print("This script will help you set up secure authentication for your dashboard.")
    print("⚠️  IMPORTANT: Change the default passwords immediately!")
    print()
    
    # Check if users.json already exists
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(users_file):
        print("❌ Users file already exists. Use manage_users.py to modify users.")
        return
    
    # Get admin credentials
    print("Setting up admin user:")
    admin_username = input("Admin username (default: admin): ").strip() or "admin"
    
    while True:
        admin_password = getpass.getpass("Admin password (min 8 chars): ")
        if len(admin_password) < 8:
            print("❌ Password must be at least 8 characters long.")
            continue
        
        confirm_password = getpass.getpass("Confirm admin password: ")
        if admin_password != confirm_password:
            print("❌ Passwords don't match. Try again.")
            continue
        
        break
    
    # Create users.json with admin user
    users = {admin_username: hash_password(admin_password)}
    
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    with open(users_file, "w") as f:
        import json
        json.dump(users, f, indent=2)
    
    print(f"✅ Admin user '{admin_username}' created successfully!")
    print()
    
    # Ask about additional users
    add_more = input("Add additional users? (y/n): ").lower().strip()
    
    if add_more == 'y':
        while True:
            username = input("Username (or 'done' to finish): ").strip()
            if username.lower() == 'done':
                break
            
            if username in users:
                print(f"❌ User '{username}' already exists.")
                continue
            
            while True:
                password = getpass.getpass(f"Password for {username} (min 8 chars): ")
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long.")
                    continue
                
                confirm_password = getpass.getpass(f"Confirm password for {username}: ")
                if password != confirm_password:
                    print("❌ Passwords don't match. Try again.")
                    continue
                
                break
            
            users[username] = hash_password(password)
            print(f"✅ User '{username}' added successfully!")
        
        # Save updated users
        users_file = os.path.join(os.path.dirname(__file__), "users.json")
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
    
    print()
    print("🎉 Authentication setup complete!")
    print()
    print("Next steps:")
    print("1. Start the dashboard: streamlit run dashboard/streamlit_app.py")
    print("2. Log in with your credentials")
    print("3. Change default passwords using: python manage_users.py change <username> <new_password>")
    print("4. Review SECURITY_GUIDE.md for best practices")

if __name__ == "__main__":
    setup_initial_auth() 