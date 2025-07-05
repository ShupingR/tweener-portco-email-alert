"""
Gmail Client Integration
=======================

Consolidated Gmail client providing both IMAP (reading) and SMTP (sending) functionality
for the Tweener Fund email tracking system.

This module handles:
- IMAP connection for reading emails from forwarders
- SMTP connection for sending alert emails
- Email parsing and content extraction
- Authentication and error handling

Usage:
    from integrations.gmail_client import GmailClient
    
    client = GmailClient()
    emails = client.fetch_emails_from_forwarders()
    client.send_alert_email(to_email, subject, body)
"""

import os
import imaplib
import smtplib
import email
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class GmailClient:
    """
    Gmail client for both reading (IMAP) and sending (SMTP) emails.
    
    Handles authentication, connection management, and email operations
    for the Tweener Fund email tracking system.
    """
    
    def __init__(self):
        """Initialize Gmail client with credentials from environment variables."""
        self.username = os.getenv('GMAIL_USERNAME')
        self.password = os.getenv('GMAIL_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Gmail credentials not found in environment variables")
        
        # Gmail server settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Forwarders to monitor for portfolio company updates
        self.forwarders = [
            'scot@tweenerfund.com',
            'scot@refibuy.ai', 
            'nikita@tweenerfund.com',
            'shuping@tweenerfund.com',
            'shuping.ruan@gmail.com'
        ]
    
    def connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Establish IMAP connection to Gmail for reading emails.
        
        Returns:
            IMAP connection object or None if connection fails
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            return mail
        except Exception as e:
            print(f"❌ Failed to connect to Gmail IMAP: {e}")
            return None
    
    def connect_smtp(self) -> Optional[smtplib.SMTP]:
        """
        Establish SMTP connection to Gmail for sending emails.
        
        Returns:
            SMTP connection object or None if connection fails
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            print(f"❌ Failed to connect to Gmail SMTP: {e}")
            return None
    
    def fetch_emails_from_forwarders(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch emails from known forwarders within the specified time range.
        
        Args:
            days_back: Number of days to look back for emails
            
        Returns:
            List of email dictionaries with parsed content
        """
        emails = []
        mail = self.connect_imap()
        
        if not mail:
            return emails
        
        try:
            mail.select('inbox')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Search for emails from forwarders
            for forwarder in self.forwarders:
                try:
                    search_criteria = f'(FROM "{forwarder}" SINCE "{since_date}")'
                    result, message_ids = mail.search(None, search_criteria)
                    
                    if result == 'OK' and message_ids[0]:
                        ids = message_ids[0].split()
                        
                        for msg_id in ids:
                            email_data = self._fetch_and_parse_email(mail, msg_id)
                            if email_data:
                                emails.append(email_data)
                                
                except Exception as e:
                    print(f"❌ Error searching emails from {forwarder}: {e}")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
        
        return emails
    
    def _fetch_and_parse_email(self, mail: imaplib.IMAP4_SSL, msg_id: bytes) -> Optional[Dict]:
        """
        Fetch and parse a single email message.
        
        Args:
            mail: IMAP connection object
            msg_id: Email message ID
            
        Returns:
            Parsed email data dictionary or None if parsing fails
        """
        try:
            result, msg_data = mail.fetch(msg_id, '(RFC822)')
            
            if result != 'OK':
                return None
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract email content
            return self._extract_email_content(email_message)
            
        except Exception as e:
            print(f"❌ Error parsing email {msg_id}: {e}")
            return None
    
    def _extract_email_content(self, email_message: email.message.EmailMessage) -> Dict:
        """
        Extract relevant content from an email message.
        
        Args:
            email_message: Parsed email message object
            
        Returns:
            Dictionary with email content and metadata
        """
        # Decode subject
        subject = ""
        if email_message["Subject"]:
            subject_parts = decode_header(email_message["Subject"])
            subject = "".join([
                part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
                for part, encoding in subject_parts
            ])
        
        # Extract basic metadata
        email_data = {
            'sender': email_message.get("From", ""),
            'subject': subject,
            'date': email_message.get("Date", ""),
            'message_id': email_message.get("Message-ID", ""),
            'body': "",
            'has_attachments': False,
            'attachments': []
        }
        
        # Extract body content
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        email_data['body'] += body
                    except:
                        pass
                elif part.get_filename():
                    # Track attachments
                    email_data['has_attachments'] = True
                    email_data['attachments'].append({
                        'filename': part.get_filename(),
                        'content_type': part.get_content_type(),
                        'size': len(part.get_payload(decode=True) or b'')
                    })
        else:
            try:
                email_data['body'] = email_message.get_payload(decode=True).decode('utf-8')
            except:
                email_data['body'] = str(email_message.get_payload())
        
        return email_data
    
    def send_alert_email(self, to_email: str, subject: str, body: str, 
                        cc_emails: List[str] = None) -> bool:
        """
        Send an alert email via SMTP.
        
        Args:
            to_email: Primary recipient email address
            subject: Email subject line
            body: Email body content
            cc_emails: Optional list of CC recipients
            
        Returns:
            True if email sent successfully, False otherwise
        """
        server = self.connect_smtp()
        
        if not server:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            recipients = [to_email] + (cc_emails or [])
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


def main():
    """Demo function showing Gmail client usage."""
    print("📧 Gmail Client Demo")
    print("=" * 30)
    
    try:
        client = GmailClient()
        
        # Test IMAP connection
        print("🔗 Testing IMAP connection...")
        emails = client.fetch_emails_from_forwarders(days_back=1)
        print(f"   Found {len(emails)} emails from last day")
        
        # Show sample email if available
        if emails:
            sample = emails[0]
            print(f"   Sample: {sample['subject'][:50]}...")
        
        print("✅ Gmail client working properly!")
        
    except Exception as e:
        print(f"❌ Gmail client error: {e}")


if __name__ == "__main__":
    main() 