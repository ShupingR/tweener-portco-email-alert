# Tweener Fund Portfolio Email Tracking System

A comprehensive, AI-powered system for tracking portfolio company email updates, extracting financial metrics, and managing communications with automated alerts.

## 🎯 **Overview**

This system monitors email updates from **151 portfolio companies**, uses **Claude AI** to analyze content and extract financial metrics, and provides automated tracking with optional alert functionality. The system focuses on **data collection and analysis** while maintaining the capability for automated reminders.

### **Key Features**
- 🤖 **AI-Powered Analysis**: Claude Sonnet 4 identifies company updates and extracts financial metrics
- 📊 **Financial Metrics Extraction**: ARR, MRR, cash balance, runway, growth rates, and more
- 📎 **Attachment Processing**: Downloads and organizes financial documents by company
- 🏢 **Portfolio Tracking**: Distinguishes between portfolio and non-portfolio companies
- 🚨 **Alert System**: Configurable reminders for missing updates (currently paused)
- 📈 **Historical Tracking**: Complete audit trail of all communications

## 🏗️ **System Architecture**

```
📁 pipeline/              # Core data processing pipeline
├── email_collector.py    # Main daily collection script
├── email_processor.py    # Claude AI email analysis
├── financial_extractor.py # Financial metrics extraction
└── config.py             # Pipeline configuration

📁 database/              # Data persistence layer
├── models.py             # Core database models
├── financial_models.py   # Financial metrics models
├── connection.py         # Database connection management
└── migrations/           # Database schema updates

📁 integrations/          # External service clients
├── gmail_client.py       # Gmail IMAP/SMTP functionality
└── claude_client.py      # Anthropic Claude AI client

📁 alerts/                # Alert system (configurable)
└── alert_manager.py      # Alert logic and email sending

📁 utils/                 # Utility functions
├── financial_formatter.py # Financial data parsing/formatting
└── data_cleaner.py       # Data deduplication utilities

📁 setup/                 # One-time setup scripts
├── gmail_oauth.py        # Gmail OAuth authentication
└── import_initial_data.py # Initial data import from CSV
```

## 🚀 **Quick Start**

### **1. Installation**
```bash
# Clone the repository
git clone <repository-url>
cd tweener-portco-email-alert

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Setup**
```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
# Required:
GMAIL_USERNAME=update@tweenerfund.com
GMAIL_PASSWORD=your_app_specific_password
ANTHROPIC_API_KEY=your_claude_api_key
```

### **3. Database Setup**
```bash
# Import initial portfolio companies and contacts
python setup/import_initial_data.py

# Set up financial metrics tables
python database/migrations/setup_financial_metrics.py
```

### **4. Gmail Authentication**
```bash
# Set up Gmail OAuth (one-time setup)
python setup/gmail_oauth.py
# Follow the browser prompts to authenticate with update@tweenerfund.com
```

### **5. Daily Email Collection**
```bash
# Test run (safe - no database changes)
./collect_emails.sh --dry-run

# Collect emails from last 7 days
./collect_emails.sh

# Collect specific time range
./collect_emails.sh --days=3
```

## 📊 **Current System Status**

### **Database Contents**
- **Portfolio Companies**: 151 companies actively tracked
- **Non-Portfolio Companies**: Companies monitored but not alerted
- **Contacts**: 138 founder/CEO contacts with email addresses
- **Email Updates**: All processed emails with full content
- **Financial Metrics**: 34+ extracted financial records from 19+ companies
- **Attachments**: Downloaded and organized by company

### **AI Analysis Capabilities**
- **Company Identification**: Automatically identifies which company an email is about
- **Portfolio Classification**: Distinguishes portfolio vs non-portfolio companies
- **Financial Extraction**: Extracts 25+ financial metrics including:
  - Revenue: MRR, ARR, QRR, total/gross/net revenue
  - Growth: MRR/ARR growth, YoY/MoM growth rates
  - Financial Health: Cash balance, burn rate, runway months
  - Business Metrics: Customer count, churn rate, team size
  - Profitability: Gross margin, EBITDA, net income

## 🔧 **Daily Usage**

### **Command Options**
```bash
# Basic collection
./collect_emails.sh                     # Last 7 days (default)
./collect_emails.sh --days=1            # Yesterday only
./collect_emails.sh --days=30           # Last month

# Safe testing
./collect_emails.sh --dry-run           # Test without saving
./collect_emails.sh --dry-run --days=1  # Test yesterday only

# Information
./collect_emails.sh --stats             # Show database statistics
```

### **Python Direct Usage**
```bash
# All shell script options work with Python directly
python pipeline/email_collector.py --days=7
python pipeline/email_collector.py --dry-run
python pipeline/email_collector.py --stats
```

### **Sample Output**
```
📧 Tweener Fund Daily Email Collector
==================================================
📧 Email: update@tweenerfund.com
🤖 Claude API: ✅ Connected

🔍 Collecting emails from last 7 days...

📊 Changes Made:
   New Companies: 0
   New Emails: 4
   New Attachments: 3

📈 Financial Metrics Extracted:
   New Records: 2
   Companies Updated: 2

✅ EMAIL COLLECTION COMPLETED
```

## 🚨 **Alert System** (Optional)

The alert system can send automated reminders when portfolio companies haven't provided updates:

### **Alert Thresholds**
- **31 days**: First reminder to founder/CEO
- **62 days**: Second reminder to founder/CEO
- **93 days**: Escalation to General Partners

### **Team Configuration**
- **GPs**: Scot Wingo, Robbie Allen
- **Partner**: Nikita Ramaswamy  
- **EIR**: Shuping Dluge

### **Enable Alerts** (Currently Paused)
```bash
# Check which companies need alerts (dry-run)
python alerts/alert_manager.py --check --dry-run

# Send actual alerts (when ready)
python alerts/alert_manager.py --send
```

## 📁 **File Organization**

### **Data Storage**
- **Database**: `tracker.db` (SQLite, excluded from git)
- **Attachments**: `attachments/{company_id}/` (organized by company)
- **Logs**: Comprehensive logging of all operations

### **Configuration Files**
- **`.env`**: Environment variables (excluded from git)
- **`env.example`**: Template for environment setup
- **`requirements.txt`**: Python dependencies
- **`collect_emails.sh`**: Main execution script

## 🔒 **Security & Privacy**

### **Protected Data**
- Email credentials and API keys (`.env`)
- Database with company information (`tracker.db`)
- Downloaded attachments (`attachments/`)
- OAuth tokens (`token.json`)

### **Git Exclusions**
```gitignore
.env
*.db
*.sqlite*
attachments/
token.json
credentials.json
financial_reports/
link_data/
```

## 🛠️ **Technical Stack**

- **Language**: Python 3.12+
- **Database**: SQLite (local) / PostgreSQL (production ready)
- **ORM**: SQLAlchemy with relationship mapping
- **AI**: Anthropic Claude Sonnet 4
- **Email**: Gmail IMAP/SMTP with OAuth2
- **Storage**: Local filesystem (cloud-ready)

## 📈 **Advanced Features**

### **Financial Metrics Dashboard**
```bash
# Generate financial reports
python utils/financial_formatter.py

# View portfolio metrics
python -c "
from database.connection import SessionLocal
from database.financial_models import FinancialMetrics
session = SessionLocal()
metrics = session.query(FinancialMetrics).count()
print(f'Total financial records: {metrics}')
"
```

### **Data Export**
```bash
# Export company data
python utils/data_cleaner.py --export

# Database queries
sqlite3 tracker.db "SELECT name, last_update_date FROM companies WHERE is_tweener_portfolio = 1;"
```

## 🔄 **Automation**

### **Cron Setup** (Optional)
```bash
# Edit crontab
crontab -e

# Add daily collection at 9 AM
0 9 * * * cd /path/to/email-alert && ./collect_emails.sh >> logs/collection.log 2>&1
```

### **Background Processing**
The system is designed for daily batch processing but can be configured for real-time monitoring.

## 🐛 **Troubleshooting**

### **Common Issues**
```bash
# Test Gmail connection
python integrations/gmail_client.py

# Test Claude API
python integrations/claude_client.py

# Check database integrity
python database/connection.py

# Verify file permissions
ls -la .env attachments/
```

### **Database Issues**
```bash
# Reset database (if needed)
rm tracker.db
python setup/import_initial_data.py
python database/migrations/setup_financial_metrics.py
```

## 📞 **Support & Development**

### **System Status**
- ✅ **Production Ready**: Core email collection and analysis
- ✅ **AI Integration**: Claude Sonnet 4 analysis working
- ✅ **Financial Extraction**: Comprehensive metrics extraction
- ✅ **Attachment Handling**: Download and organization
- ⏸️ **Alert System**: Available but currently paused
- 🔄 **Continuous Improvement**: Regular updates and enhancements

### **Next Steps**
1. **Production Deployment**: Enable alert system when ready
2. **Dashboard Development**: Web interface for monitoring
3. **Advanced Analytics**: Trend analysis and reporting
4. **Integration Expansion**: Slack, Teams, or other platforms

---

**Status**: ✅ **Production Ready for Data Collection**  
**Last Updated**: June 2025  
**Maintained By**: Tweener Fund Team

For questions or issues, check the troubleshooting section above or review the individual module documentation in each directory's `__init__.py` files. 