"""
Gmail SMTP-based email ingestion using credentials from .env file
This uses IMAP to read emails and SMTP to send alerts
"""

import os
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import SessionLocal
from models import Company, Contact, EmailUpdate, Attachment, Alert

# Load environment variables
load_dotenv()

class GmailSMTPService:
    def __init__(self):
        self.gmail_username = os.getenv('GMAIL_USERNAME')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')
        self.gp_emails = os.getenv('GP_EMAILS', '').split(',')
        
        if not self.gmail_username or not self.gmail_password:
            raise ValueError("Gmail credentials not found in .env file")
        
        print(f"📧 Configured for: {self.gmail_username}")
        print(f"👥 GP emails: {', '.join(self.gp_emails)}")
    
    def connect_imap(self):
        """Connect to Gmail IMAP"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_username, self.gmail_password)
            print("✅ Connected to Gmail IMAP")
            return mail
        except Exception as e:
            print(f"❌ Failed to connect to Gmail IMAP: {e}")
            return None
    
    def connect_smtp(self):
        """Connect to Gmail SMTP for sending emails"""
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_username, self.gmail_password)
            print("✅ Connected to Gmail SMTP")
            return server
        except Exception as e:
            print(f"❌ Failed to connect to Gmail SMTP: {e}")
            return None
    
    def fetch_emails(self):
        """Fetch emails from portfolio companies"""
        print("🔍 Fetching emails from portfolio companies...")
        
        mail = self.connect_imap()
        if not mail:
            return False
        
        session = SessionLocal()
        
        try:
            # Get all contact emails
            contacts = session.query(Contact).filter(Contact.email_bounced == False).all()
            contact_emails = [c.email.lower() for c in contacts]
            
            print(f"📋 Searching for emails from {len(contact_emails)} contacts...")
            
            # Select inbox
            mail.select('inbox')
            
            total_processed = 0
            
            # Search for emails from each contact
            for contact in contacts:
                try:
                    # Search for emails from this sender
                    search_criteria = f'FROM "{contact.email}"'
                    result, message_ids = mail.search(None, search_criteria)
                    
                    if result != 'OK':
                        continue
                    
                    message_ids = message_ids[0].split()
                    
                    if not message_ids:
                        continue
                    
                    print(f"  📧 Found {len(message_ids)} emails from {contact.email} ({contact.company.name})")
                    
                    # Process each email
                    for msg_id in message_ids[-10:]:  # Process last 10 emails
                        try:
                            result, msg_data = mail.fetch(msg_id, '(RFC822)')
                            
                            if result != 'OK':
                                continue
                            
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Extract email details
                            subject = email_message['Subject'] or ''
                            date_str = email_message['Date'] or ''
                            sender = email_message['From'] or ''
                            
                            # Parse date
                            try:
                                email_date = email.utils.parsedate_to_datetime(date_str)
                            except:
                                email_date = datetime.now()
                            
                            # Extract sender email
                            if '<' in sender and '>' in sender:
                                sender_email = sender.split('<')[1].split('>')[0].strip().lower()
                            else:
                                sender_email = sender.strip().lower()
                            
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
                            body = self.extract_email_body(email_message)
                            
                            # Check for attachments
                            has_attachments = False
                            attachment_count = 0
                            
                            for part in email_message.walk():
                                if part.get_content_disposition() == 'attachment':
                                    has_attachments = True
                                    attachment_count += 1
                                    
                                    # Save attachment
                                    filename = part.get_filename()
                                    if filename:
                                        self.save_attachment(part, filename, contact.company_id, session)
                            
                            # Create email update record
                            email_update = EmailUpdate(
                                company_id=contact.company_id,
                                sender=sender_email,
                                subject=subject,
                                body=body,
                                date=email_date,
                                has_attachments=has_attachments
                            )
                            
                            session.add(email_update)
                            total_processed += 1
                            
                            if attachment_count > 0:
                                print(f"    📎 Processed email with {attachment_count} attachments: {subject[:50]}...")
                            else:
                                print(f"    📄 Processed email: {subject[:50]}...")
                            
                        except Exception as e:
                            print(f"    ❌ Error processing email: {e}")
                            continue
                
                except Exception as e:
                    print(f"  ❌ Error searching emails for {contact.email}: {e}")
                    continue
            
            session.commit()
            print(f"\n✅ Successfully processed {total_processed} emails")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            session.rollback()
            return False
            
        finally:
            session.close()
            mail.close()
            mail.logout()
    
    def extract_email_body(self, email_message):
        """Extract text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
                    except:
                        continue
                elif content_type == "text/html" and "attachment" not in content_disposition and not body:
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8')
                        # Convert HTML to text (basic)
                        body = html_body.replace('<br>', '\n').replace('</p>', '\n')
                        # Remove HTML tags (basic)
                        import re
                        body = re.sub('<[^<]+?>', '', body)
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8')
            except:
                body = str(email_message.get_payload())
        
        return body[:10000]  # Limit body size
    
    def save_attachment(self, part, filename, company_id, session):
        """Save email attachment to local storage"""
        try:
            # Create attachments directory if it doesn't exist
            attachments_dir = "attachments"
            if not os.path.exists(attachments_dir):
                os.makedirs(attachments_dir)
            
            # Create company-specific subdirectory
            company_dir = os.path.join(attachments_dir, str(company_id))
            if not os.path.exists(company_dir):
                os.makedirs(company_dir)
            
            # Save file with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(company_dir, safe_filename)
            
            # Save attachment
            with open(file_path, 'wb') as f:
                f.write(part.get_payload(decode=True))
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create attachment record (will be linked to email update later)
            attachment = Attachment(
                filename=filename,
                path=file_path,
                file_size=file_size
            )
            
            print(f"      💾 Saved attachment: {filename} ({file_size} bytes)")
            
            return attachment
            
        except Exception as e:
            print(f"      ❌ Error saving attachment {filename}: {e}")
            return None
    
    def send_alert_email(self, to_email, subject, body):
        """Send alert email using SMTP"""
        try:
            server = self.connect_smtp()
            if not server:
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.gmail_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Sent alert email to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False


def test_gmail_connection():
    """Test Gmail SMTP connection"""
    print("🧪 Testing Gmail SMTP connection...")
    
    try:
        gmail_service = GmailSMTPService()
        
        # Test IMAP connection
        mail = gmail_service.connect_imap()
        if mail:
            # Select inbox to test
            mail.select('inbox')
            result, messages = mail.search(None, 'ALL')
            if result == 'OK':
                print(f"✅ IMAP connection successful - found {len(messages[0].split()) if messages[0] else 0} messages")
            mail.close()
            mail.logout()
        
        # Test SMTP connection
        server = gmail_service.connect_smtp()
        if server:
            server.quit()
            print("✅ SMTP connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main():
    """Main function to run email ingestion"""
    print("📧 Tweener Fund Email Ingestion (SMTP)")
    print("=" * 50)
    
    try:
        # Test connection first
        if not test_gmail_connection():
            print("❌ Gmail connection failed. Check your .env file credentials.")
            return
        
        # Create Gmail service
        gmail_service = GmailSMTPService()
        
        # Fetch emails
        success = gmail_service.fetch_emails()
        
        if success:
            print("\n✅ Email ingestion completed successfully!")
            
            # Show summary
            session = SessionLocal()
            email_count = session.query(EmailUpdate).count()
            company_count = session.query(Company).join(EmailUpdate).distinct().count()
            
            print(f"📊 Summary:")
            print(f"   Total emails: {email_count}")
            print(f"   Companies with emails: {company_count}")
            
            session.close()
        else:
            print("\n❌ Email ingestion failed.")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 