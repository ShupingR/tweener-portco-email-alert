"""
Gmail API Setup Script for update@tweenerfund.com
This script will help you authenticate with Gmail API
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'  # For sending alert emails
]

def setup_gmail_credentials():
    """Set up Gmail API credentials"""
    print("Gmail API Setup for update@tweenerfund.com")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing project")
        print("3. Enable Gmail API")
        print("4. Go to 'Credentials' > 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("5. Choose 'Desktop application'")
        print("6. Download the JSON file and save it as 'credentials.json' in this directory")
        print("\nOnce you have credentials.json, run this script again.")
        return False
    
    print("✅ Found credentials.json")
    
    creds = None
    
    # Check if token.json exists (previous authentication)
    if os.path.exists('token.json'):
        print("📁 Found existing token.json")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully")
            except Exception as e:
                print(f"❌ Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            print("🔐 Starting OAuth flow...")
            print("⚠️  IMPORTANT: Make sure to log in with update@tweenerfund.com when prompted!")
            print("   This will open a browser window for authentication.")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("💾 Saved credentials to token.json")
    
    return creds


def test_gmail_connection(creds):
    """Test the Gmail connection"""
    print("\n" + "=" * 50)
    print("Testing Gmail Connection")
    print("=" * 50)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile to verify connection
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')
        
        print(f"✅ Connected to Gmail successfully!")
        print(f"📧 Email address: {email_address}")
        
        if email_address != 'update@tweenerfund.com':
            print(f"⚠️  WARNING: Connected to {email_address} instead of update@tweenerfund.com")
            print("   Please make sure you're logged in with the correct account.")
        
        # Get message count
        messages = service.users().messages().list(userId='me', maxResults=1).execute()
        total_messages = messages.get('resultSizeEstimate', 0)
        print(f"📊 Total messages in inbox: {total_messages}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Gmail: {e}")
        return False


def test_portfolio_emails(creds):
    """Test searching for emails from portfolio companies"""
    print("\n" + "=" * 50)
    print("Testing Portfolio Company Email Search")
    print("=" * 50)
    
    try:
        from db import SessionLocal
        from models import Contact
        
        service = build('gmail', 'v1', credentials=creds)
        session = SessionLocal()
        
        # Get a few sample contacts
        sample_contacts = session.query(Contact).limit(5).all()
        
        if not sample_contacts:
            print("❌ No contacts found in database")
            return False
        
        print(f"🔍 Searching for emails from {len(sample_contacts)} sample contacts...")
        
        total_found = 0
        for contact in sample_contacts:
            try:
                # Search for emails from this contact
                query = f'from:{contact.email}'
                results = service.users().messages().list(
                    userId='me', 
                    q=query,
                    maxResults=10
                ).execute()
                
                messages = results.get('messages', [])
                total_found += len(messages)
                
                if messages:
                    print(f"  📧 {contact.email} ({contact.company.name}): {len(messages)} emails")
                else:
                    print(f"  📪 {contact.email} ({contact.company.name}): No emails found")
                    
            except Exception as e:
                print(f"  ❌ Error searching {contact.email}: {e}")
        
        print(f"\n📊 Total emails found from sample contacts: {total_found}")
        
        if total_found == 0:
            print("💡 This could mean:")
            print("   - Portfolio companies haven't sent updates to this email yet")
            print("   - They're sending to a different email address")
            print("   - Updates are in a different folder/label")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing portfolio emails: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Gmail API Setup for Tweener Fund Email Tracker")
    print("=" * 60)
    
    # Install required packages
    print("📦 Checking required packages...")
    try:
        import google.auth
        import googleapiclient
        print("✅ Google API packages are installed")
    except ImportError:
        print("❌ Missing required packages!")
        print("Please run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return
    
    # Setup credentials
    creds = setup_gmail_credentials()
    if not creds:
        print("❌ Setup failed. Please check the instructions above.")
        return
    
    # Test connection
    if not test_gmail_connection(creds):
        print("❌ Connection test failed.")
        return
    
    # Test portfolio email search
    test_portfolio_emails(creds)
    
    print("\n" + "=" * 60)
    print("🎉 Gmail API setup complete!")
    print("✅ You can now run the email ingestion script")
    print("📝 Next steps:")
    print("   1. Run: python gmail_ingest.py")
    print("   2. Set up scheduled email checking")
    print("   3. Configure alert system")


if __name__ == "__main__":
    main() 