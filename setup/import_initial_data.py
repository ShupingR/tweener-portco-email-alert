"""
Data import script to load companies and contacts from CSV files
"""

import pandas as pd
from datetime import datetime
from database.connection import SessionLocal, init_db
from database.models import Company, Contact
import re


def clean_string(value):
    """Clean and normalize string values"""
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()


def import_from_founder_emails(founder_emails_csv):
    print(f"Importing companies and contacts from {founder_emails_csv}")
    df = pd.read_csv(founder_emails_csv)
    session = SessionLocal()
    # Clear all existing companies and contacts
    session.query(Contact).delete()
    session.query(Company).delete()
    session.commit()
    imported_companies = 0
    imported_contacts = 0
    for idx, row in df.iterrows():
        company_name = clean_string(row.get('Company Name'))
        status = clean_string(row.get('Status'))
        emails = clean_string(row.get('Email'))
        if not company_name:
            continue
        # Create company
        company = Company(name=company_name, description=None, is_tweener_portfolio=True)
        imported_companies += 1
        if status:
            company.investment_state = status.lower()
        session.add(company)
        session.flush()  # get company.id
        # Parse emails (can be comma-separated)
        if emails:
            for email in re.split(r'[;,]', emails):
                email = clean_string(email)
                if not email:
                    continue
                contact = Contact(company_id=company.id, email=email)
                imported_contacts += 1
                session.add(contact)
    session.commit()
    print(f"Imported {imported_companies} companies and {imported_contacts} contacts from founder_emails.csv")
    session.close()


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
    
    print("\nImporting data from founder_emails.csv ...")
    import_from_founder_emails("scot_data/founder_emails.csv")
    
    print("\nTesting imported data...")
    test_data()
    
    print("\nData import complete!")
