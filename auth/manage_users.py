#!/usr/bin/env python3
"""
User Management Script for Tweener Insights Dashboard
"""

import sys
import os
import hashlib
import json
from typing import Dict, List

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import auth_config directly since this is a standalone script
import sys
import os
sys.path.append(os.path.dirname(__file__))
from auth_config import hash_password, get_all_users

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users() -> Dict[str, str]:
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users: Dict[str, str]):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(username: str, password: str):
    """Add a new user"""
    users = load_users()
    
    if username in users:
        print(f"❌ User '{username}' already exists!")
        return False
    
    users[username] = hash_password(password)
    save_users(users)
    print(f"✅ User '{username}' added successfully!")
    return True

def remove_user(username: str):
    """Remove a user"""
    users = load_users()
    
    if username not in users:
        print(f"❌ User '{username}' not found!")
        return False
    
    del users[username]
    save_users(users)
    print(f"✅ User '{username}' removed successfully!")
    return True

def list_users():
    """List all users"""
    users = load_users()
    
    if not users:
        print("📝 No users found.")
        return
    
    print("📝 Current users:")
    for username in users.keys():
        print(f"  • {username}")

def change_password(username: str, new_password: str):
    """Change a user's password"""
    users = load_users()
    
    if username not in users:
        print(f"❌ User '{username}' not found!")
        return False
    
    users[username] = hash_password(new_password)
    save_users(users)
    print(f"✅ Password for '{username}' changed successfully!")
    return True

def main():
    """Main function for user management"""
    print("🔐 Tweener Insights - User Management")
    print("=====================================")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_users.py add <username> <password>")
        print("  python manage_users.py remove <username>")
        print("  python manage_users.py list")
        print("  python manage_users.py change <username> <new_password>")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        add_user(username, password)
    
    elif command == "remove" and len(sys.argv) == 3:
        username = sys.argv[2]
        remove_user(username)
    
    elif command == "list":
        list_users()
    
    elif command == "change" and len(sys.argv) == 4:
        username = sys.argv[2]
        new_password = sys.argv[3]
        change_password(username, new_password)
    
    else:
        print("❌ Invalid command or arguments!")
        print("Use 'python manage_users.py' for help.")

if __name__ == "__main__":
    main() 