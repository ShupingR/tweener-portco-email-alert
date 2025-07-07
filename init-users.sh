#!/bin/bash

# Initialize User Credentials for SummerAI Dashboard
# This script creates the initial user database in Google Cloud Secret Manager

PROJECT_ID="famous-rhythm-465100-p6"
SECRET_NAME="USER_CREDENTIALS"

echo "🔐 Initializing SummerAI User Management System"
echo "📊 Project: $PROJECT_ID"
echo "🔑 Secret: $SECRET_NAME"
echo "=========================================="

# Create the user credentials JSON
cat > /tmp/user_credentials.json << 'EOF'
{
  "users": {
    "admin": {
      "password_hash": "b46de898d2edca77a10f2bcffa2b8c29115b33853460babcc24c29f963d2f7c6",
      "role": "admin",
      "email": "shuping@summerai.biz",
      "full_name": "Shu Ping (Admin)",
      "created_date": "2025-07-06T22:45:00",
      "last_login": null,
      "active": true
    },
    "viewer": {
      "password_hash": "05200f915c39c162ee65b513bb6c5b4574358215998c4a0677ae4bde85d4345b",
      "role": "viewer",
      "email": "viewer@summerai.biz",
      "full_name": "Portfolio Viewer",
      "created_date": "2025-07-06T22:45:00",
      "last_login": null,
      "active": true
    },
    "analyst": {
      "password_hash": "761d8bdb783b30972e96b5bef0f6380578f72471f5bd599bb5b7a6a73e608495",
      "role": "analyst", 
      "email": "analyst@summerai.biz",
      "full_name": "Portfolio Analyst",
      "created_date": "2025-07-06T22:45:00",
      "last_login": null,
      "active": true
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
EOF

echo "📝 Creating user credentials secret..."

# Create the secret (will fail if exists, which is fine)
gcloud secrets create $SECRET_NAME --data-file=/tmp/user_credentials.json 2>/dev/null || {
    echo "Secret already exists, updating with new version..."
    gcloud secrets versions add $SECRET_NAME --data-file=/tmp/user_credentials.json
}

# Clean up
rm /tmp/user_credentials.json

echo "✅ User management system initialized!"
echo ""
echo "🔑 Default User Accounts Created:"
echo "1. **Administrator**"
echo "   - Username: admin"
echo "   - Password: TweenerAdmin2025"
echo "   - Full access to all features"
echo ""
echo "2. **Viewer**"
echo "   - Username: viewer"
echo "   - Password: ViewerAccess2025"
echo "   - Read-only access"
echo ""
echo "3. **Analyst**"
echo "   - Username: analyst"
echo "   - Password: AnalystAccess2025"
echo "   - Read and write access"
echo ""
echo "🚀 You can now manage users through the dashboard's User Management page!"
