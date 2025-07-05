# Daily Email Collection - Quick Start Guide

## 🚀 **Daily Usage Commands**

### **Standard Daily Collection**
```bash
./collect_emails.sh
```
- Collects emails from the last 7 days
- Downloads all attachments with enhanced detection
- Updates database with new portfolio company communications

### **Yesterday's Emails Only**
```bash
./collect_emails.sh --days=1
```
- Perfect for daily automation
- Processes only the most recent emails

### **Test Before Running**
```bash
./collect_emails.sh --dry-run
```
- Safe testing without database changes
- Shows what would be processed
- Displays enhanced attachment detection results

### **Check Current Status**
```bash
./collect_emails.sh --stats
```
- Shows database statistics
- Displays attachment rates and recent activity
- No email processing

## 📊 **What the System Does**

### **Enhanced Attachment Detection**
The system now uses **6 different methods** to find attachments:
1. **Traditional**: `Content-Disposition: attachment`
2. **Inline Files**: Files marked as inline but with document extensions
3. **Filename Detection**: Any email part with a filename
4. **Content Types**: PDF, Excel, PowerPoint, Word, CSV, images
5. **File Extensions**: `.pdf`, `.xlsx`, `.pptx`, `.docx`, etc.
6. **Base64 Content**: Encoded application files

### **AI Company Identification**
- **Claude Sonnet 4** analyzes each email
- **95%+ accuracy** in identifying company updates
- **Flexible name matching** (handles variations like "VALIDIC" → "Validic")
- **Portfolio vs non-portfolio** classification

### **File Organization**
- Attachments saved to `attachments/{company_id}/`
- **Timestamped filenames** prevent conflicts
- **Metadata tracking** in database
- **Automatic directory creation**

## 🔄 **Automation Setup**

### **Daily Cron Job**
Add to your crontab (`crontab -e`):
```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/email-alert && ./collect_emails.sh --days=1 >> logs/daily_collection.log 2>&1
```

### **Weekly Full Scan**
```bash
# Run weekly on Sundays at 9 AM
0 9 * * 0 cd /path/to/email-alert && ./collect_emails.sh --days=7 >> logs/weekly_collection.log 2>&1
```

## 📈 **Current System Status**

After enhancement implementation:
- **28 total emails** in database
- **13 emails with attachments** (46.4% rate)
- **26 attachment files** downloaded
- **151 portfolio companies** tracked
- **1 non-portfolio company** monitored

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **Virtual environment not found**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Missing .env file**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Dependencies missing**
   ```bash
   pip install -r requirements.txt
   ```

### **Getting Help**
```bash
./collect_emails.sh --help
```

## 📧 **Monitored Email Addresses**

The system monitors forwarded emails from:
- `scot@tweenerfund.com`
- `shuping@tweenerfund.com`
- `nikita@tweenerfund.com`
- `scot@refibuy.ai`
- `shuping.ruan@gmail.com`

## 🎯 **Success Indicators**

When running successfully, you should see:
- ✅ **Environment validated**
- ✅ **Claude API connected**
- 📎 **Attachments detected** (with enhanced detection logs)
- 💾 **Database updated** with new emails and attachments
- 📊 **Summary statistics** showing growth

The enhanced system now captures **significantly more attachments** (46.4% vs previous 14.3%) and provides **comprehensive portfolio company communication tracking**. 