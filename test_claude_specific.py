"""
Test script to specifically check Claude's analysis of Validic, Equity Shift, and Trayecto emails
"""

import os
import imaplib
import email
from dotenv import load_dotenv
from claude_email_processor import ClaudeEmailProcessor
from db import SessionLocal
from models import Company

load_dotenv()

def test_specific_companies():
    """Test Claude analysis on specific problematic companies"""
    print("🧪 Testing Claude analysis on specific companies")
    print("=" * 60)
    
    processor = ClaudeEmailProcessor()
    session = SessionLocal()
    
    try:
        # Get portfolio companies
        portfolio_companies = session.query(Company).all()
        
        # Check if our target companies are in the list
        target_companies = ['Validic', 'Equity Shift', 'Trayecto']
        found_companies = []
        
        for target in target_companies:
            for company in portfolio_companies:
                if target.lower() in company.name.lower():
                    found_companies.append(company.name)
                    print(f"✅ Found: {company.name}")
        
        print(f"\nFound {len(found_companies)} target companies in database")
        
        # Fetch specific emails
        mail = processor.connect_imap()
        if not mail:
            return
        
        mail.select('inbox')
        
        # Search for specific emails
        test_subjects = [
            'VALIDIC',
            'Equity Shift',
            'Trayecto'
        ]
        
        for subject_search in test_subjects:
            print(f"\n🔍 Searching for emails with '{subject_search}'...")
            
            try:
                search_criteria = f'SUBJECT "{subject_search}"'
                result, message_ids = mail.search(None, search_criteria)
                
                if result == 'OK' and message_ids[0]:
                    message_ids = message_ids[0].split()
                    print(f"   Found {len(message_ids)} emails")
                    
                    # Analyze the first email
                    if message_ids:
                        msg_id = message_ids[0]
                        result, msg_data = mail.fetch(msg_id, '(RFC822)')
                        
                        if result == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Extract content
                            email_content = processor.extract_email_content(email_message)
                            print(f"   Subject: {email_content['subject']}")
                            
                            # Analyze with Claude
                            analysis = processor.analyze_with_claude(email_content, portfolio_companies)
                            
                            if analysis:
                                print(f"   🤖 Claude Analysis:")
                                print(f"      Company update: {analysis.get('is_company_update', False)}")
                                print(f"      Company: {analysis.get('company_name', 'None')}")
                                print(f"      Confidence: {analysis.get('confidence', 0):.2f}")
                                print(f"      Reasoning: {analysis.get('reasoning', 'N/A')[:150]}...")
                            else:
                                print(f"   ❌ Claude analysis failed")
                else:
                    print(f"   No emails found")
                    
            except Exception as e:
                print(f"   ❌ Error searching for {subject_search}: {e}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_specific_companies() 