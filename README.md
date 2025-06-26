# Tweener Fund Email Tracker

A comprehensive system to track email updates from portfolio companies and send automated reminders when updates are missing.

## 🎯 Purpose

Track all email updates from 151 portfolio companies, store emails with attachments, and automatically remind founders when updates are overdue (1 month + 1 day, 2 months + 2 days) with escalation to general partners after 3 months + 3 days.

## 📊 Current Status

✅ **Completed:**
- Database models and schema
- Data import from CSV files (151 companies, 138 contacts)
- Gmail API integration setup
- Email ingestion framework
- Deduplication system
- Test framework

🔄 **Ready for Setup:**
- Gmail API authentication for `update@tweenerfund.com`
- Real email ingestion
- Alert/reminder system
- Scheduling automation

## 🗂️ Database Structure

- **Companies**: 151 portfolio companies with investment details
- **Contacts**: 138 founder/CEO contacts with email addresses
- **EmailUpdates**: Stores all incoming emails with body, subject, date
- **Attachments**: Tracks email attachments (stored locally)
- **Alerts**: Manages reminder/escalation system

## 📁 Project Files

### Core System
- `models.py` - Database models (SQLAlchemy)
- `db.py` - Database connection and setup
- `import_data.py` - Import companies and contacts from CSV
- `deduplicate.py` - Remove duplicate companies

### Gmail Integration
- `setup_gmail.py` - Gmail API authentication setup
- `gmail_ingest.py` - Email ingestion from Gmail
- `GMAIL_SETUP_GUIDE.md` - Step-by-step setup instructions

### Testing & Utilities
- `test_system.py` - Comprehensive system testing
- `requirements.txt` - Python dependencies

### Data Sources
- `scot_data/Triangle Tweener Fund_Lifetime_Investments.csv` - Portfolio companies
- `scot_data/ContactExport-export-c64323f753.csv` - Contact information

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database and Import Data
```bash
python import_data.py
```

### 3. Set Up Gmail API (for update@tweenerfund.com)
Follow the detailed guide in `GMAIL_SETUP_GUIDE.md`:
```bash
python setup_gmail.py
```

### 4. Run Email Ingestion
```bash
python gmail_ingest.py
```

### 5. Test the System
```bash
python test_system.py
```

## 📧 Gmail Setup Summary

The system connects to `update@tweenerfund.com` to:
- Search for emails from all 138 portfolio company contacts
- Extract email body, subject, date, and attachments
- Store everything in the database for tracking

**Required:** Google Cloud Console setup with Gmail API enabled and OAuth credentials.

## 🔔 Alert System (Next Phase)

The reminder system will:
- **1 Month + 1 Day**: Email reminder to founder
- **2 Months + 2 Days**: Second reminder to founder  
- **3 Months + 3 Days**: Escalation email to general partners

## 📈 Current Data

- **151 Portfolio Companies** (deduplicated from 412)
- **138 Contacts** with email addresses
- **Sample Companies**: Wrangle, Trio Labs, Wander Maps, ArenaCX, XComP Analytics
- **Ready for Email Tracking**: All contacts loaded and mapped to companies

## 🛠️ Technical Stack

- **Database**: SQLite (local) / PostgreSQL (production)
- **Framework**: SQLAlchemy ORM
- **Email**: Gmail API with OAuth2
- **Language**: Python 3.12
- **Storage**: Local file system for attachments

## 📋 Next Steps

1. **Complete Gmail Setup**
   - Follow `GMAIL_SETUP_GUIDE.md`
   - Authenticate with `update@tweenerfund.com`
   - Test email ingestion

2. **Build Alert System**
   - Create reminder email templates
   - Implement scheduling logic
   - Set up email sending functionality

3. **Add Scheduling**
   - Daily email checking
   - Automated reminder sending
   - Background job processing

4. **Create Dashboard**
   - Web interface for monitoring
   - Company update status
   - Alert management

5. **Deploy to Google Cloud**
   - Cloud SQL database
   - Cloud Storage for attachments
   - Cloud Functions for scheduling

## 🔒 Security Notes

- Keep `credentials.json` and `token.json` secure
- Never commit authentication files to version control
- Use environment variables for production deployment
- Consider encrypted storage for sensitive data

## 📞 Support

For issues or questions:
1. Check the troubleshooting sections in the guides
2. Verify all setup steps were completed
3. Test with the provided test scripts
4. Check Google Cloud Console for API limits/quotas

---

**Status**: Local prototype ready for Gmail API setup and testing. 