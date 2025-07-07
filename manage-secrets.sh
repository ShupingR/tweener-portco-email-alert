#!/bin/bash

# SummerAI Secret Manager Helper Script
# This script helps manage secrets in Google Cloud Secret Manager

set -e

PROJECT_ID="famous-rhythm-465100-p6"

echo "🔐 SummerAI Secret Manager - Manage your secrets securely"
echo "📊 Project: $PROJECT_ID"
echo "=========================================="

# Function to update a secret
update_secret() {
    local secret_name=$1
    local description=$2
    
    echo "🔒 Updating secret: $secret_name"
    echo "📝 Description: $description"
    read -s -p "Enter the value for $secret_name: " secret_value
    echo
    
    # Update the secret
    echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    echo "✅ Secret $secret_name updated successfully!"
    echo
}

# Function to create or update all secrets
setup_all_secrets() {
    echo "📋 Setting up all secrets..."
    echo
    
    update_secret "GMAIL_USERNAME" "Gmail username for email alerts"
    update_secret "GMAIL_PASSWORD" "Gmail app password (not regular password)"
    update_secret "ANTHROPIC_API_KEY" "Anthropic Claude API key"
    update_secret "ADMIN_PASSWORD" "Admin dashboard password"
    
    # Generate a random session secret
    session_secret=$(openssl rand -base64 32)
    echo -n "$session_secret" | gcloud secrets versions add SESSION_SECRET --data-file=-
    echo "✅ Generated and set SESSION_SECRET automatically!"
    echo
}

# Function to view secrets (names only, not values)
list_secrets() {
    echo "📋 Current secrets in Secret Manager:"
    gcloud secrets list --format="table(name,createTime)"
}

# Function to test secret access
test_secret() {
    local secret_name=$1
    echo "🧪 Testing access to secret: $secret_name"
    
    if gcloud secrets versions access latest --secret="$secret_name" > /dev/null 2>&1; then
        echo "✅ Secret $secret_name is accessible"
        # Show first 3 characters for verification (safely)
        first_chars=$(gcloud secrets versions access latest --secret="$secret_name" | head -c 3)
        echo "🔍 First 3 characters: $first_chars***"
    else
        echo "❌ Cannot access secret $secret_name"
    fi
    echo
}

# Function to delete a secret
delete_secret() {
    local secret_name=$1
    echo "⚠️  WARNING: This will permanently delete the secret: $secret_name"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] ]]; then
        gcloud secrets delete $secret_name
        echo "🗑️  Secret $secret_name deleted"
    else
        echo "❌ Deletion cancelled"
    fi
    echo
}

# Main menu
show_menu() {
    echo "Choose an option:"
    echo "1. Setup all secrets"
    echo "2. Update individual secret"
    echo "3. List all secrets"
    echo "4. Test secret access"
    echo "5. Delete a secret"
    echo "6. Exit"
    echo
}

# Main script logic
if [[ $# -eq 0 ]]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        echo
        
        case $choice in
            1)
                setup_all_secrets
                ;;
            2)
                read -p "Enter secret name: " secret_name
                read -p "Enter description: " description
                update_secret "$secret_name" "$description"
                ;;
            3)
                list_secrets
                echo
                ;;
            4)
                read -p "Enter secret name to test: " secret_name
                test_secret "$secret_name"
                ;;
            5)
                read -p "Enter secret name to delete: " secret_name
                delete_secret "$secret_name"
                ;;
            6)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid choice. Please try again."
                echo
                ;;
        esac
    done
else
    # Command line mode
    case $1 in
        "setup")
            setup_all_secrets
            ;;
        "list")
            list_secrets
            ;;
        "test")
            if [[ -n $2 ]]; then
                test_secret "$2"
            else
                echo "❌ Please provide a secret name to test"
            fi
            ;;
        "update")
            if [[ -n $2 ]] && [[ -n $3 ]]; then
                update_secret "$2" "$3"
            else
                echo "❌ Usage: $0 update <secret_name> <description>"
            fi
            ;;
        *)
            echo "❌ Usage: $0 [setup|list|test <secret_name>|update <secret_name> <description>]"
            ;;
    esac
fi
