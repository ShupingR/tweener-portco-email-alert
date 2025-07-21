"""
Claude-powered email processor to identify company updates from forwarded emails
This script searches for emails from Scot Wingo and Shuping Dluge, then uses Claude
to identify which ones are company updates and extract relevant information.
"""

import os
import re
import json
import imaplib
import email
from datetime import datetime, timedelta
from dotenv import load_dotenv
import anthropic
from database.connection import SessionLocal
from database.models import Company, Contact, EmailUpdate, Attachment
from email.header import decode_header

# Load environment variables
load_dotenv()

class ClaudeEmailProcessor:
    def __init__(self):
        """Initialize the Claude email processor"""
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.email_username = os.getenv("GMAIL_USERNAME")
        self.email_password = os.getenv("GMAIL_PASSWORD")
        
        # Initialize Claude
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.claude_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
        
        # Forwarders to monitor
        self.forwarders = [
            "scot@tweenerfund.com",
            "scot@refibuy.ai", 
            "nikita@tweenerfund.com",
            "shuping@tweenerfund.com",
            "shuping.ruan@gmail.com"
        ]
        
        print(f"📧 Configured for: {self.email_username}")
        print(f"🤖 Claude API: {'✅ Connected' if self.claude_api_key else '❌ Not configured'}")
        print(f"👥 Monitoring forwards from: {', '.join(self.forwarders)}")

    def connect_imap(self):
        """Connect to Gmail IMAP"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_username, self.email_password)
            return mail
        except Exception as e:
            print(f"❌ IMAP connection failed: {e}")
            return None
    
    def fetch_forwarded_emails(self, days_back=30):
        """Fetch emails from known forwarders"""
        print(f"🔍 Fetching emails from forwarders (last {days_back} days)...")
        
        mail = self.connect_imap()
        if not mail:
            return []
        
        try:
            mail.select('inbox')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            forwarded_emails = []
            
            for forwarder in self.forwarders:
                try:
                    # Search for emails from this forwarder
                    search_criteria = f'(FROM "{forwarder}" SINCE "{since_date}")'
                    result, message_ids = mail.search(None, search_criteria)
                    
                    if result != 'OK':
                        continue
                    
                    message_ids = message_ids[0].split()
                    
                    if message_ids:
                        print(f"  📧 Found {len(message_ids)} emails from {forwarder}")
                        
                        # Fetch each email
                        for msg_id in message_ids:
                            try:
                                result, msg_data = mail.fetch(msg_id, '(RFC822)')
                                if result == 'OK':
                                    email_body = msg_data[0][1]
                                    email_message = email.message_from_bytes(email_body)
                                    forwarded_emails.append({
                                        'forwarder': forwarder,
                                        'message': email_message,
                                        'msg_id': msg_id.decode()
                                    })
                            except Exception as e:
                                print(f"    ❌ Error fetching email: {e}")
                                continue
                    
                except Exception as e:
                    print(f"  ❌ Error searching emails from {forwarder}: {e}")
                    continue
            
            print(f"📬 Total forwarded emails found: {len(forwarded_emails)}")
            return forwarded_emails
            
        except Exception as e:
            print(f"❌ Error fetching forwarded emails: {e}")
            return []
            
        finally:
            mail.close()
            mail.logout()

    def process_emails_time_range(self, start_time, end_time):
        """Process emails for a specific time range"""
        # Calculate days back from time range
        time_diff = datetime.now() - start_time
        days_back = max(1, int(time_diff.days) + 1)
        
        # Fetch emails and filter by time range
        forwarded_emails = self.fetch_forwarded_emails(days_back)
        
        # Filter emails by time range
        filtered_emails = []
        for email_data in forwarded_emails:
            email_content = self.extract_email_content(email_data['message'])
            email_date = email_content['date']
            if start_time <= email_date <= end_time:
                filtered_emails.append(email_data)
        
        print(f"📬 Found {len(filtered_emails)} emails in time range")
        
        # Process the filtered emails
        self._process_email_list(filtered_emails)

    def process_emails(self, days_back=30):
        """Process emails from the last N days"""
        forwarded_emails = self.fetch_forwarded_emails(days_back)
        self._process_email_list(forwarded_emails)

    def _process_email_list(self, email_list):
        """Process a list of emails"""
        session = SessionLocal()
        portfolio_companies = session.query(Company).all()
        
        try:
            for email_data in email_list:
                self._process_single_email(email_data, portfolio_companies, session)
        finally:
            session.close()
    
    def extract_email_content(self, email_message):
        """Extract content from email message including aggressive attachment detection"""
        # Decode subject
        subject = ""
        if email_message["subject"]:
            subject_header = decode_header(email_message["subject"])
            subject_parts = []
            for part, encoding in subject_header:
                if isinstance(part, bytes):
                    try:
                        if encoding:
                            subject_parts.append(part.decode(encoding))
                        else:
                            subject_parts.append(part.decode('utf-8'))
                    except:
                        subject_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    subject_parts.append(str(part))
            subject = ''.join(subject_parts)
        
        # Get sender and date
        sender = email_message.get("From", "")
        date_str = email_message.get("Date", "")
        
        # Parse date
        try:
            date_obj = email.utils.parsedate_tz(date_str)
            if date_obj:
                timestamp = email.utils.mktime_tz(date_obj)
                date = datetime.fromtimestamp(timestamp)
            else:
                date = datetime.now()
        except:
            date = datetime.now()
        
        # Extract body and check for attachments with AGGRESSIVE detection
        body = ""
        attachments = []
        has_attachments = False
        
        # Define attachment-friendly content types
        attachment_content_types = {
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint', 
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/zip',
            'application/x-zip-compressed',
            'application/octet-stream',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/tiff',
            'text/csv'
        }
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                filename = part.get_filename()
                
                # AGGRESSIVE ATTACHMENT DETECTION
                is_attachment = False
                
                # Method 1: Traditional attachment detection
                if part.get_content_disposition() == 'attachment':
                    is_attachment = True
                
                # Method 2: Check for inline dispositions that might be attachments
                elif 'attachment' in content_disposition.lower():
                    is_attachment = True
                
                # Method 3: Check for filename presence (strong indicator)
                elif filename and filename.strip():
                    is_attachment = True
                
                # Method 4: Check for attachment-friendly content types
                elif content_type in attachment_content_types:
                    is_attachment = True
                
                # Method 5: Check for inline files with file extensions
                elif content_disposition and 'inline' in content_disposition.lower() and filename:
                    # Check if filename has a document extension
                    file_extensions = ['.pdf', '.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.doc', 
                                     '.csv', '.zip', '.png', '.jpg', '.jpeg', '.gif', '.tiff']
                    if any(filename.lower().endswith(ext) for ext in file_extensions):
                        is_attachment = True
                
                # Method 6: Check for base64 encoded content that might be files
                elif (content_type.startswith('application/') and 
                      part.get('Content-Transfer-Encoding') == 'base64'):
                    is_attachment = True
                
                # Process if identified as attachment
                if is_attachment:
                    has_attachments = True
                    
                    # Handle filename decoding more robustly
                    if not filename:
                        # Try to extract filename from content-disposition
                        if 'filename=' in content_disposition:
                            filename_match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', content_disposition)
                            if filename_match:
                                filename = filename_match.group(1)
                    
                    if filename:
                        # Decode filename if needed
                        decoded_filename = decode_header(filename)
                        if decoded_filename and decoded_filename[0]:
                            if isinstance(decoded_filename[0][0], bytes):
                                try:
                                    encoding = decoded_filename[0][1] or 'utf-8'
                                    filename = decoded_filename[0][0].decode(encoding)
                                except:
                                    filename = decoded_filename[0][0].decode('utf-8', errors='ignore')
                            else:
                                filename = decoded_filename[0][0]
                        
                        # Clean filename
                        filename = filename.strip().strip('"\'')
                        
                        # Generate filename if still missing
                        if not filename:
                            ext_map = {
                                'application/pdf': '.pdf',
                                'application/vnd.ms-excel': '.xls',
                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                                'application/vnd.ms-powerpoint': '.ppt',
                                'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
                                'application/msword': '.doc',
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                                'text/csv': '.csv',
                                'image/jpeg': '.jpg',
                                'image/png': '.png'
                            }
                            extension = ext_map.get(content_type, '.bin')
                            filename = f"attachment_{len(attachments) + 1}{extension}"
                        
                        attachments.append({
                            'part': part,
                            'filename': filename,
                            'content_type': content_type,
                            'detection_method': 'aggressive'
                        })
                        
                        print(f"      🔍 Found attachment: {filename} ({content_type})")
                
                # Extract text content (only from non-attachment parts)
                elif content_type == "text/plain" and not is_attachment:
                    try:
                        part_body = part.get_payload(decode=True)
                        if part_body:
                            body = part_body.decode('utf-8')
                    except:
                        continue
                elif content_type == "text/html" and not is_attachment and not body:
                    try:
                        html_body = part.get_payload(decode=True)
                        if html_body:
                            html_content = html_body.decode('utf-8')
                            # Basic HTML to text conversion
                            body = html_content.replace('<br>', '\n').replace('</p>', '\n')
                            body = re.sub('<[^<]+?>', '', body)
                    except:
                        continue
        else:
            # Single part message - check if it might be an attachment
            content_type = email_message.get_content_type()
            filename = email_message.get_filename()
            
            if filename or content_type in attachment_content_types:
                has_attachments = True
                if not filename:
                    filename = f"single_part_attachment.{content_type.split('/')[-1]}"
                
                attachments.append({
                    'part': email_message,
                    'filename': filename,
                    'content_type': content_type,
                    'detection_method': 'single_part'
                })
            else:
                # Regular text content
                try:
                    body_content = email_message.get_payload(decode=True)
                    if body_content:
                        body = body_content.decode('utf-8')
                except:
                    body = str(email_message.get_payload())
        
        # Log attachment detection results
        if has_attachments:
            print(f"      📎 Detected {len(attachments)} attachment(s) using aggressive detection")
        
        return {
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body[:10000],  # Limit body size
            'has_attachments': has_attachments,
            'attachments': attachments
        }
    
    def analyze_with_claude(self, email_content, portfolio_companies):
        """Use Claude to analyze if this is a company update and extract information"""
        
        # Create company list for Claude with variations
        company_entries = []
        for company in portfolio_companies:
            entry = f"- {company.name}"
            # Add common variations
            if "Inc" not in company.name and "LLC" not in company.name:
                entry += f" (may also appear as {company.name} Inc, {company.name} LLC)"
            company_entries.append(entry)
        
        # Include ALL companies, not just first 100
        company_list = "\n".join(company_entries)
        
        prompt = f"""You are analyzing an email to determine if it contains a company update from any company. This email was forwarded by a venture capital fund partner.

KNOWN PORTFOLIO COMPANIES (be flexible with company name variations):
{company_list}

EMAIL TO ANALYZE:
Subject: {email_content['subject']}
From: {email_content['sender']}
Date: {email_content['date']}

Body:
{email_content['body']}

ANALYSIS INSTRUCTIONS:
1. Determine if this email contains an update from ANY company (portfolio or non-portfolio)
2. Look for forwarded emails, investor updates, monthly reports, quarterly updates, etc.
3. Be VERY FLEXIBLE with company names - companies may appear with variations like:
   - "VALIDIC" matches "Validic"
   - "Equity Shift Inc." matches "Equity Shift" 
   - "Trayecto Letter" matches "Trayecto"
4. If it's from a company in the KNOWN PORTFOLIO COMPANIES list above, mark is_portfolio_company as true
5. If it's from a company NOT in the list but still appears to be a legitimate company update, mark is_portfolio_company as false
6. Extract the company name (use exact name from portfolio list if it matches, otherwise use the name as it appears in the email)
7. IMPORTANT: If you see ANY company name that could reasonably match one from the list, consider it a portfolio company match

Please respond in JSON format:
{{
    "is_company_update": true/false,
    "company_name": "company name (exact from portfolio list if matches, otherwise as appears in email)",
    "is_portfolio_company": true/false,
    "confidence": 0.0-1.0,
    "original_sender": "email address of the actual company sender if identifiable",
    "update_type": "monthly/quarterly/special/funding/other",
    "key_topics": ["list", "of", "main", "topics"],
    "summary": "brief summary of the update content",
    "reasoning": "why you classified this as a company update or not, and whether it's portfolio or non-portfolio"
}}

CRITICAL: 
- Be extremely flexible with company name matching for portfolio companies
- For non-portfolio companies, still capture legitimate business updates
- Only respond with valid JSON."""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            # Parse Claude's response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                print(f"⚠️  Could not parse Claude response as JSON: {response_text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing with Claude: {e}")
            return None
    
    def find_company_by_name(self, company_name, session):
        """Find company in database by name (fuzzy matching)"""
        if not company_name:
            return None
        
        # Clean the company name for matching
        clean_name = company_name.lower().strip()
        clean_name = re.sub(r'\b(inc|llc|corp|corporation|ltd)\b\.?', '', clean_name).strip()
        
        companies = session.query(Company).all()
        
        # Try exact match first
        for comp in companies:
            if comp.name.lower() == clean_name:
                return comp
        
        # Try direct substring match
        for comp in companies:
            comp_clean = comp.name.lower().strip()
            comp_clean = re.sub(r'\b(inc|llc|corp|corporation|ltd)\b\.?', '', comp_clean).strip()
            
            if comp_clean == clean_name:
                return comp
        
        # Try partial matching
        for comp in companies:
            comp_clean = comp.name.lower().strip()
            comp_clean = re.sub(r'\b(inc|llc|corp|corporation|ltd)\b\.?', '', comp_clean).strip()
            
            if (clean_name in comp_clean or comp_clean in clean_name):
                return comp
        
        # Last resort: very fuzzy matching
        for comp in companies:
            if (company_name.lower() in comp.name.lower() or 
                comp.name.lower() in company_name.lower()):
                return comp
        
        return None
    
    def save_company_email(self, email_content, analysis, forwarder, session):
        """Save identified company email to database"""
        try:
            company_name = analysis['company_name']
            is_portfolio = analysis.get('is_portfolio_company', True)
            
            # Find existing company or create new one
            company = self.find_company_by_name(company_name, session)
            
            if not company:
                # Create new company record
                print(f"🆕 Creating new company record: {company_name}")
                company = Company(
                    name=company_name,
                    is_tweener_portfolio=is_portfolio,
                    last_update_date=email_content['date']
                )
                session.add(company)
                session.flush()  # Get the company.id
                
                if is_portfolio:
                    print(f"   ✅ Added as Tweener portfolio company")
                else:
                    print(f"   📝 Added as non-Tweener company (tracking only)")
            else:
                # Update existing company
                if not is_portfolio and company.is_tweener_portfolio:
                    print(f"⚠️  Warning: {company.name} was marked as portfolio company but analysis suggests non-portfolio")
                elif is_portfolio and not company.is_tweener_portfolio:
                    print(f"🔄 Updating {company.name} to portfolio company status")
                    company.is_tweener_portfolio = True
            
            # Check if email already exists
            existing = session.query(EmailUpdate).filter(
                EmailUpdate.company_id == company.id,
                EmailUpdate.subject == email_content['subject'],
                EmailUpdate.date == email_content['date']
            ).first()
            
            if existing:
                print(f"📧 Email already exists for {company.name}")
                return False
            
            # Create email update record
            email_update = EmailUpdate(
                company_id=company.id,
                sender=analysis.get('original_sender', forwarder),
                subject=email_content['subject'],
                body=email_content['body'],
                date=email_content['date'],
                has_attachments=email_content['has_attachments']
            )
            
            session.add(email_update)
            session.flush()  # Get the email_update.id
            
            # Process attachments if any
            attachment_count = 0
            if email_content['has_attachments'] and email_content['attachments']:
                for attachment_data in email_content['attachments']:
                    attachment = self.save_attachment(attachment_data, company.id, session)
                    if attachment:
                        attachment.email_update_id = email_update.id
                        session.add(attachment)
                        attachment_count += 1
            
            # Update company's last update date
            company.last_update_date = email_content['date']
            
            session.commit()
            
            # Display results
            portfolio_status = "Portfolio" if company.is_tweener_portfolio else "Non-Portfolio"
            print(f"✅ Saved email update for {company.name} ({portfolio_status})")
            print(f"   Subject: {email_content['subject'][:60]}...")
            print(f"   Type: {analysis.get('update_type', 'unknown')}")
            print(f"   Topics: {', '.join(analysis.get('key_topics', [])[:3])}")
            if attachment_count > 0:
                print(f"   📎 Attachments: {attachment_count} files saved")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving email: {e}")
            session.rollback()
            return False
    
    def save_attachment(self, attachment_data, company_id, session):
        """Save email attachment to local storage"""
        try:
            part = attachment_data['part']
            filename = attachment_data['filename']
            
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
            
            # Create attachment record
            attachment = Attachment(
                filename=filename,
                path=file_path,
                file_size=file_size
            )
            
            print(f"      💾 Saved attachment: {filename} ({file_size:,} bytes)")
            
            return attachment
            
        except Exception as e:
            print(f"      ❌ Error saving attachment {attachment_data.get('filename', 'unknown')}: {e}")
            return None
    
    def process_emails(self, days_back=30):
        """Process emails from the last N days"""
        forwarded_emails = self.fetch_forwarded_emails(days_back)
        self._process_email_list(forwarded_emails)

    def _process_single_email(self, email_data, portfolio_companies, session):
        """Process a single email"""
        try:
            print(f"\n🔍 Analyzing email from {email_data['forwarder']}...")
            
            # Extract email content
            email_content = self.extract_email_content(email_data['message'])
            print(f"   Subject: {email_content['subject'][:60]}...")
            
            # Analyze with Claude
            analysis = self.analyze_with_claude(email_content, portfolio_companies)
            
            if not analysis:
                print("   ❌ Claude analysis failed")
                return False
            
            print(f"   🤖 Claude analysis:")
            print(f"      Company update: {analysis.get('is_company_update', False)}")
            print(f"      Confidence: {analysis.get('confidence', 0):.2f}")
            
            if analysis.get('is_company_update') and analysis.get('confidence', 0) > 0.7:
                print(f"      Company: {analysis.get('company_name', 'Unknown')}")
                print(f"      Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")
                
                # Save to database
                return self.save_company_email(email_content, analysis, email_data['forwarder'], session)
            else:
                print(f"      ❌ Not a company update or low confidence")
                if analysis.get('reasoning'):
                    print(f"      Reasoning: {analysis.get('reasoning')[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Error processing email: {e}")
            return False


def main():
    """Main function"""
    print("🤖 Claude-Powered Email Update Processor")
    print("=" * 60)
    
    try:
        processor = ClaudeEmailProcessor()
        processor.process_emails(days_back=30)
        
        print("\n✅ Email processing complete!")
        
        # Show summary
        session = SessionLocal()
        total_emails = session.query(EmailUpdate).count()
        companies_with_emails = session.query(Company).join(EmailUpdate).distinct().count()
        
        print(f"\n📈 Database Summary:")
        print(f"   Total emails: {total_emails}")
        print(f"   Companies with emails: {companies_with_emails}")
        
        # Show recent emails
        recent_emails = session.query(EmailUpdate).order_by(EmailUpdate.date.desc()).limit(5).all()
        if recent_emails:
            print(f"\n📧 Recent emails:")
            for email in recent_emails:
                print(f"   - {email.company.name}: {email.subject[:50]}... ({email.date.strftime('%Y-%m-%d')})")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 