# Daily Email Collector for Tweener Fund

A streamlined, production-ready email collection system that gathers portfolio company updates daily without sending any alerts.

## 🎯 **Purpose**

This system focuses solely on **data gathering** - collecting, analyzing, and storing portfolio company email updates with attachments. The alert functionality is separate and can be enabled later.

## 🚀 **Quick Start**

### **Simple Daily Collection**
```bash
# Collect emails from the last 7 days (default)
./collect_emails.sh

# Or use Python directly
python daily_email_collector.py
```

### **Test Run (Safe)**
```bash
# See what would be collected without making changes
./collect_emails.sh --dry-run
python daily_email_collector.py --dry-run
```

### **Check Current Status**
```bash
# View database statistics
./collect_emails.sh --stats
python daily_email_collector.py --stats
```

## 📋 **Command Options**

### **Python Script Options**
```bash
# Basic usage
python daily_email_collector.py                    # Last 7 days
python daily_email_collector.py --days=3           # Last 3 days
python daily_email_collector.py --days=1           # Yesterday only

# Safe testing
python daily_email_collector.py --dry-run          # Test without saving
python daily_email_collector.py --days=1 --dry-run # Test 1 day

# Information only
python daily_email_collector.py --stats            # Show statistics
```

### **Shell Script Options**
```bash
# All Python options work with the shell script
./collect_emails.sh --days=3
./collect_emails.sh --dry-run
./collect_emails.sh --stats
```

## 🔧 **What It Does**

### **Email Collection**
- ✅ Connects to Gmail IMAP (update@tweenerfund.com)
- ✅ Monitors emails from configured forwarders
- ✅ Processes emails from last N days (configurable)

### **AI Analysis**
- ✅ Uses Claude Sonnet 4 to analyze each email
- ✅ Identifies portfolio company updates vs other emails
- ✅ Distinguishes between portfolio and non-portfolio companies
- ✅ Extracts company names, confidence scores, and key topics

### **Data Storage**
- ✅ Saves email content to SQLite database
- ✅ Downloads and organizes attachments by company
- ✅ Tracks both portfolio and non-portfolio companies
- ✅ Prevents duplicate processing
- ✅ Maintains complete historical record

## 📊 **Output Examples**

### **Normal Run**
```
📧 Tweener Fund Daily Email Collector
==================================================
📧 Email: update@tweenerfund.com
🤖 Claude API: ✅ Connected

🔍 Collecting emails from last 7 days...

📊 Changes Made:
   New Companies: 0
   New Emails: 3
   New Attachments: 4

✅ EMAIL COLLECTION COMPLETED
```

### **Dry Run**
```
🧪 DRY RUN MODE - No changes will be made to database
📬 Found 3 emails to analyze
🧪 DRY RUN COMPLETE - Would have processed 3 emails
```

### **Statistics Only**
```
📊 Current Database Statistics:
   Portfolio Companies: 151
   Non-Portfolio Companies: 1
   Total Companies: 152
   Total Email Updates: 173
   Total Attachments: 5
   Recent Emails (7 days): 5
```

## ⚙️ **Configuration**

### **Environment Variables** (.env)
```bash
# Required
GMAIL_USERNAME=update@tweenerfund.com
GMAIL_PASSWORD=your_app_specific_password
ANTHROPIC_API_KEY=your_claude_api_key

# Optional
DATABASE_URL=sqlite:///tracker.db
```

## 🔄 **Daily Automation**

### **Manual Daily Run**
```bash
# Run this command daily
./collect_emails.sh
```

### **Cron Automation** (Optional)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/email-alert && ./collect_emails.sh >> logs/collection.log 2>&1
```

## 🛡️ **Safety Features**

- **Dry Run Mode**: Test without making database changes
- **Duplicate Prevention**: Automatically skips processed emails
- **Error Handling**: Continues processing if individual emails fail
- **Data Protection**: Sensitive files excluded from git

## 📁 **File Structure**

```
email-alert/
├── daily_email_collector.py    # Main collection script
├── collect_emails.sh           # Shell wrapper script
├── collector_config.py         # Configuration settings
├── claude_email_processor.py   # Email analysis engine
├── models.py                   # Database schema
├── db.py                       # Database connection
├── .env                        # Environment variables (not in git)
├── env.example                 # Environment template
├── requirements.txt            # Python dependencies
├── tracker.db                  # SQLite database (not in git)
└── attachments/                # Downloaded files (not in git)
```

---

**Ready to use!** Start with `./collect_emails.sh --dry-run` to test, then `./collect_emails.sh` for daily collection.
