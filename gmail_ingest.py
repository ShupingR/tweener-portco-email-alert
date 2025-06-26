"""
Gmail ingestion script (basic version for testing)
"""

import os
import base64
from datetime import datetime
from db import SessionLocal
from models import Company, Contact, EmailUpdate, Attachment

# For now, this is a placeholder since we need Gmail API setup
# We'll create a test version that simulates email processing

def test_gmail_connection():
    """Test Gmail API connection (placeholder)"""
    print("Testing Gmail connection...")
    print("Note: Gmail API setup required for actual email ingestion")
    print("Required steps:")
    print("1. Enable Gmail API in Google Cloud Console")
    print("2. Download credentials.json file")
    print("3. Run OAuth flow to get token.json")
    print("4. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    return False


def simulate_email_processing():
    """Simulate processing emails for testing"""
    print("Simulating email processing...")
    
    session = SessionLocal()
    
    # Get some contacts to simulate emails from
    contacts = session.query(Contact).limit(5).all()
    
    for contact in contacts:
        # Create a simulated email update
        email_update = EmailUpdate(
            company_id=contact.company_id,
            sender=contact.email,
            subject=f"Monthly Update from {contact.company.name}",
            body=f"This is a simulated monthly update from {contact.first_name} {contact.last_name} at {contact.company.name}.\n\nKey metrics:\n- Revenue: Growing\n- Team size: Expanding\n- Challenges: Fundraising",
            date=datetime.now(),
            has_attachments=False
        )
        
        session.add(email_update)
        print(f"Simulated email from {contact.email} for {contact.company.name}")
    
    session.commit()
    session.close()
    print("Simulated email processing complete!")


def get_gmail_service():
    """Get Gmail service (requires OAuth setup)"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        if not os.path.exists('token.json'):
            print("❌ Gmail token not found.")
            print("Please run: python setup_gmail.py")
            return None
        
        # Load credentials
        creds = Credentials.from_authorized_user_file(
            'token.json', 
            ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        )
        
        # Refresh if expired
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired credentials...")
                creds.refresh(Request())
                # Save refreshed credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("✅ Credentials refreshed")
            else:
                print("❌ Gmail credentials expired or invalid.")
                print("Please run: python setup_gmail.py")
                return None
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Verify connection
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')
        print(f"✅ Connected to Gmail: {email_address}")
        
        return service
        
    except ImportError:
        print("❌ Google API client not installed.")
        print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return None
    except Exception as e:
        print(f"❌ Error connecting to Gmail: {e}")
        return None


def fetch_real_emails():
    """Fetch real emails from Gmail (requires setup)"""
    service = get_gmail_service()
    if not service:
        return False
    
    session = SessionLocal()
    
    try:
        # Get all contact emails to search for
        contacts = session.query(Contact).filter(Contact.email_bounced == False).all()
        contact_emails = [c.email for c in contacts]
        
        print(f"Searching for emails from {len(contact_emails)} contacts...")
        
        # Build Gmail search query
        email_queries = []
        for i in range(0, len(contact_emails), 10):  # Process in batches
            batch = contact_emails[i:i+10]
            query = ' OR '.join([f'from:{email}' for email in batch])
            email_queries.append(query)
        
        total_processed = 0
        
        for query in email_queries:
            try:
                # Search for messages
                results = service.users().messages().list(
                    userId='me', 
                    q=query,
                    maxResults=50
                ).execute()
                
                messages = results.get('messages', [])
                print(f"Found {len(messages)} messages for batch query")
                
                for msg in messages:
                    # Get full message details
                    msg_detail = service.users().messages().get(
                        userId='me', 
                        id=msg['id'], 
                        format='full'
                    ).execute()
                    
                    # Parse headers
                    headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
                    sender = headers.get('From', '')
                    subject = headers.get('Subject', '')
                    date_str = headers.get('Date', '')
                    
                    # Parse date
                    try:
                        from email.utils import parsedate_to_datetime
                        email_date = parsedate_to_datetime(date_str)
                    except:
                        email_date = datetime.now()
                    
                    # Extract sender email
                    if '<' in sender and '>' in sender:
                        sender_email = sender.split('<')[1].split('>')[0].strip().lower()
                    else:
                        sender_email = sender.strip().lower()
                    
                    # Find company
                    contact = session.query(Contact).filter(
                        Contact.email == sender_email
                    ).first()
                    
                    if not contact:
                        continue
                    
                    # Check if already processed
                    existing = session.query(EmailUpdate).filter(
                        EmailUpdate.company_id == contact.company_id,
                        EmailUpdate.sender == sender_email,
                        EmailUpdate.subject == subject,
                        EmailUpdate.date == email_date
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Extract body
                    body = ''
                    if 'data' in msg_detail['payload'].get('body', {}):
                        body_data = msg_detail['payload']['body']['data']
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    
                    # Create email update record
                    email_update = EmailUpdate(
                        company_id=contact.company_id,
                        sender=sender_email,
                        subject=subject,
                        body=body,
                        date=email_date,
                        has_attachments=False  # TODO: Handle attachments
                    )
                    
                    session.add(email_update)
                    total_processed += 1
                    
                    print(f"Processed email from {sender_email}: {subject[:50]}...")
                
            except Exception as e:
                print(f"Error processing batch: {e}")
                continue
        
        session.commit()
        print(f"Successfully processed {total_processed} emails")
        
    except Exception as e:
        print(f"Error fetching emails: {e}")
        session.rollback()
        
    finally:
        session.close()
    
    return True


def test_email_data():
    """Test the email data in database"""
    session = SessionLocal()
    
    email_count = session.query(EmailUpdate).count()
    print(f"\nEmail Data Summary:")
    print(f"Total emails: {email_count}")
    
    if email_count > 0:
        print(f"\nSample Emails:")
        emails = session.query(EmailUpdate).limit(5).all()
        for email in emails:
            print(f"  - From: {email.sender}")
            print(f"    Company: {email.company.name}")
            print(f"    Subject: {email.subject[:50]}...")
            print(f"    Date: {email.date}")
            print()
    
    session.close()


if __name__ == "__main__":
    print("📧 Tweener Fund Email Ingestion")
    print("=" * 50)
    
    # Check if Gmail is set up
    if os.path.exists('token.json'):
        print("🔍 Attempting to fetch real emails from update@tweenerfund.com...")
        success = fetch_real_emails()
        
        if success:
            print("\n📊 Email ingestion completed successfully!")
        else:
            print("\n⚠️  Email ingestion failed, running simulation instead...")
            simulate_email_processing()
    else:
        print("⚠️  Gmail not set up yet.")
        print("Please run: python setup_gmail.py")
        print("\nRunning simulation for testing...")
        simulate_email_processing()
    
    print("\n📈 Current email data summary:")
    test_email_data()
    
    print("\n✅ Email ingestion process complete!")
