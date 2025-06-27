"""
Deduplication script to remove duplicate companies and fix relationships
"""

from db import SessionLocal
from models import Company, Contact, EmailUpdate
from collections import defaultdict


def deduplicate_companies():
    """Remove duplicate companies and reassign contacts/emails"""
    print("Starting company deduplication...")
    
    session = SessionLocal()
    
    try:
        # Get all companies
        companies = session.query(Company).all()
        print(f"Found {len(companies)} total companies")
        
        # Group companies by name (case-insensitive)
        company_groups = defaultdict(list)
        for company in companies:
            key = company.name.lower().strip() if company.name else "unnamed"
            company_groups[key].append(company)
        
        print(f"Found {len(company_groups)} unique company names")
        
        # Process each group
        companies_to_delete = []
        reassignments = []
        
        for company_name, group in company_groups.items():
            if len(group) <= 1:
                continue  # No duplicates
            
            print(f"\nProcessing duplicates for: {group[0].name} ({len(group)} duplicates)")
            
            # Choose the "best" company to keep (most complete data)
            def score_company(company):
                score = 0
                if company.legal_name: score += 1
                if company.website: score += 1
                if company.founders: score += 1
                if company.description: score += 1
                if company.investment_amount: score += 1
                return score
            
            # Sort by score (descending) and take the first one
            group.sort(key=score_company, reverse=True)
            company_to_keep = group[0]
            companies_to_duplicate = group[1:]
            
            print(f"  Keeping: ID {company_to_keep.id} (score: {score_company(company_to_keep)})")
            print(f"  Removing: {[c.id for c in companies_to_duplicate]}")
            
            # Reassign contacts and emails from duplicates to the kept company
            for duplicate in companies_to_duplicate:
                # Reassign contacts
                contacts = session.query(Contact).filter(Contact.company_id == duplicate.id).all()
                for contact in contacts:
                    # Check if this contact already exists for the kept company
                    existing_contact = session.query(Contact).filter(
                        Contact.company_id == company_to_keep.id,
                        Contact.email == contact.email
                    ).first()
                    
                    if existing_contact:
                        # Merge contact data if needed
                        if not existing_contact.first_name and contact.first_name:
                            existing_contact.first_name = contact.first_name
                        if not existing_contact.last_name and contact.last_name:
                            existing_contact.last_name = contact.last_name
                        if not existing_contact.job_title and contact.job_title:
                            existing_contact.job_title = contact.job_title
                        if contact.is_primary:
                            existing_contact.is_primary = True
                        
                        # Delete the duplicate contact
                        session.delete(contact)
                        print(f"    Merged duplicate contact: {contact.email}")
                    else:
                        # Reassign to kept company
                        contact.company_id = company_to_keep.id
                        print(f"    Reassigned contact: {contact.email}")
                
                # Reassign emails
                emails = session.query(EmailUpdate).filter(EmailUpdate.company_id == duplicate.id).all()
                for email in emails:
                    email.company_id = company_to_keep.id
                
                if emails:
                    print(f"    Reassigned {len(emails)} emails")
                
                companies_to_delete.append(duplicate)
        
        # Delete duplicate companies
        print(f"\nDeleting {len(companies_to_delete)} duplicate companies...")
        for company in companies_to_delete:
            session.delete(company)
        
        # Commit changes
        session.commit()
        
        # Verify results
        final_count = session.query(Company).count()
        contact_count = session.query(Contact).count()
        email_count = session.query(EmailUpdate).count()
        
        print(f"\nDeduplication complete!")
        print(f"Companies after deduplication: {final_count}")
        print(f"Contacts: {contact_count}")
        print(f"Emails: {email_count}")
        
        return True
        
    except Exception as e:
        print(f"Error during deduplication: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()


def verify_deduplication():
    """Verify that deduplication worked correctly"""
    print("\nVerifying deduplication...")
    
    session = SessionLocal()
    
    try:
        companies = session.query(Company).all()
        names = [c.name.lower().strip() for c in companies if c.name]
        
        # Check for remaining duplicates
        from collections import Counter
        name_counts = Counter(names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            print(f"⚠️  Still have {len(duplicates)} duplicate company names:")
            for name, count in list(duplicates.items())[:5]:
                print(f"  - {name}: {count} times")
        else:
            print("✓ No duplicate company names found")
        
        # Show sample companies with contacts
        print(f"\nSample companies with contacts:")
        companies_with_contacts = session.query(Company).join(Contact).distinct().limit(5).all()
        
        for company in companies_with_contacts:
            print(f"  - {company.name}: {len(company.contacts)} contacts")
        
        return len(duplicates) == 0
        
    except Exception as e:
        print(f"Error during verification: {e}")
        return False
        
    finally:
        session.close()


def main():
    """Run deduplication process"""
    print("COMPANY DEDUPLICATION")
    print("=" * 50)
    
    success = deduplicate_companies()
    
    if success:
        verify_deduplication()
        print("\n✓ Deduplication completed successfully!")
    else:
        print("\n✗ Deduplication failed. Check the errors above.")


if __name__ == "__main__":
    main() 