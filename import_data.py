"""
Data import script to load companies and contacts from CSV files
"""

import pandas as pd
from datetime import datetime
from db import SessionLocal, init_db
from models import Company, Contact


def clean_string(value):
    """Clean and normalize string values"""
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()


def import_companies(companies_csv):
    """Import companies from CSV file"""
    print(f"Importing companies from {companies_csv}")
    
    try:
        # Try different encodings for the CSV file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(companies_csv, encoding=encoding)
                print(f"Successfully read companies CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Could not read companies CSV with any supported encoding")
            
        print(f"Found {len(df)} companies in CSV")
        
        session = SessionLocal()
        imported_count = 0
        
        for index, row in df.iterrows():
            try:
                company = Company(
                    name=clean_string(row['Company Name']),
                    legal_name=clean_string(row.get('Company Legal Name')),
                    website=clean_string(row.get('Company Website')),
                    fund=clean_string(row.get('Fund')),
                    investment_amount=clean_string(row.get('Investment Amount')),
                    investment_state=clean_string(row.get('Investment State')),
                    completion_date=clean_string(row.get('Completion Date')),
                    founders=clean_string(row.get('Founders')),
                    description=clean_string(row.get('Company Description'))
                )
                
                session.add(company)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"Imported {imported_count} companies...")
                
            except Exception as e:
                print(f"Error importing company at row {index}: {e}")
                continue
        
        session.commit()
        print(f"Successfully imported {imported_count} companies")
        session.close()
        
    except Exception as e:
        print(f"Error importing companies: {e}")
        raise


def import_contacts(contacts_csv):
    """Import contacts from CSV file"""
    print(f"Importing contacts from {contacts_csv}")
    
    try:
        # Try different encodings for the CSV file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(contacts_csv, encoding=encoding)
                print(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Could not read CSV with any supported encoding")
            
        print(f"Found {len(df)} contacts in CSV")
        
        session = SessionLocal()
        
        # Create a mapping of company names to IDs
        companies = session.query(Company).all()
        company_name_to_id = {}
        
        for company in companies:
            # Try multiple variations for matching
            variations = [
                company.name.lower().strip(),
                company.legal_name.lower().strip() if company.legal_name else None,
                company.name.lower().replace(' ', '').strip(),
                company.name.lower().replace(',', '').replace('.', '').strip()
            ]
            
            for variation in variations:
                if variation:
                    company_name_to_id[variation] = company.id
        
        print(f"Created mapping for {len(company_name_to_id)} company name variations")
        
        imported_count = 0
        unmatched_companies = set()
        
        for index, row in df.iterrows():
            try:
                company_name = clean_string(row.get('Company Name'))
                if not company_name:
                    continue
                
                # Try to find matching company
                company_id = None
                
                # Direct match
                company_id = company_name_to_id.get(company_name.lower().strip())
                
                # Try partial matches if direct match fails
                if not company_id:
                    for stored_name, stored_id in company_name_to_id.items():
                        if (company_name.lower() in stored_name or 
                            stored_name in company_name.lower()):
                            company_id = stored_id
                            break
                
                if not company_id:
                    unmatched_companies.add(company_name)
                    continue
                
                # Check if email exists
                email_address = clean_string(row.get('E-mail Address'))
                if not email_address:
                    continue
                
                # Check for TTF_CEO tag to mark as primary
                is_primary = False
                for col in df.columns:
                    if 'TTF_CEO' in col and pd.notna(row.get(col)):
                        is_primary = True
                        break
                
                # Check for email bounced tag
                email_bounced = False
                for col in df.columns:
                    if 'Email Bounced' in col and pd.notna(row.get(col)):
                        email_bounced = True
                        break
                
                contact = Contact(
                    company_id=company_id,
                    first_name=clean_string(row.get('First Name')),
                    last_name=clean_string(row.get('Last Name')),
                    email=email_address.lower().strip(),
                    job_title=clean_string(row.get('Job Title')),
                    is_primary=is_primary,
                    email_bounced=email_bounced
                )
                
                session.add(contact)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"Imported {imported_count} contacts...")
                
            except Exception as e:
                print(f"Error importing contact at row {index}: {e}")
                continue
        
        session.commit()
        print(f"Successfully imported {imported_count} contacts")
        
        if unmatched_companies:
            print(f"Could not match {len(unmatched_companies)} companies:")
            for company in list(unmatched_companies)[:10]:  # Show first 10
                print(f"  - {company}")
            if len(unmatched_companies) > 10:
                print(f"  ... and {len(unmatched_companies) - 10} more")
        
        session.close()
        
    except Exception as e:
        print(f"Error importing contacts: {e}")
        raise


def test_data():
    """Test the imported data"""
    session = SessionLocal()
    
    company_count = session.query(Company).count()
    contact_count = session.query(Contact).count()
    
    print(f"\nData Import Summary:")
    print(f"Companies: {company_count}")
    print(f"Contacts: {contact_count}")
    
    # Show sample companies
    print(f"\nSample Companies:")
    companies = session.query(Company).limit(5).all()
    for company in companies:
        contact_count = len(company.contacts)
        print(f"  - {company.name} ({contact_count} contacts)")
    
    # Show sample contacts
    print(f"\nSample Contacts:")
    contacts = session.query(Contact).limit(5).all()
    for contact in contacts:
        print(f"  - {contact.first_name} {contact.last_name} ({contact.email}) - {contact.company.name}")
    
    session.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("\nImporting data...")
    import_companies("scot_data/Triangle Tweener Fund_Lifetime_Investments.csv")
    import_contacts("scot_data/ContactExport-export-c64323f753.csv")
    
    print("\nTesting imported data...")
    test_data()
    
    print("\nData import complete!")
