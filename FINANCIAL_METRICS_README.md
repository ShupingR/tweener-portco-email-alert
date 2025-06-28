# Financial Metrics Extraction System

This system automatically extracts key financial metrics from portfolio company email updates and attachments using Claude AI, then stores them in a structured database for analysis and reporting.

## 🎯 Overview

The Financial Metrics Extraction System:
- **Analyzes** email content and attachments (PDF, Excel, PowerPoint) from portfolio companies
- **Extracts** 25+ financial metrics using Claude Sonnet 4 AI
- **Stores** structured data in SQLite database with proper relationships
- **Provides** command-line tools for processing and exporting data
- **Tracks** extraction confidence and data sources

## 📊 Extracted Metrics

### Revenue Metrics
- **MRR** (Monthly Recurring Revenue)
- **ARR** (Annual Recurring Revenue) 
- **QRR** (Quarterly Recurring Revenue)
- **Total Revenue**, **Gross Revenue**, **Net Revenue**

### Growth Metrics
- **MRR Growth**, **ARR Growth**
- **Year-over-Year Growth**, **Month-over-Month Growth**

### Financial Health
- **Cash Balance**, **Net Burn**, **Gross Burn**
- **Runway** (months of cash remaining)

### Profitability
- **Gross Margin**, **EBITDA**, **EBITDA Margin**
- **Net Income/Loss**

### Customer Metrics
- **Customer Count**, **New Customers**, **Churn Rate**
- **LTV** (Lifetime Value), **CAC** (Customer Acquisition Cost)

### Operational Metrics
- **Team Size**, **Bookings**, **Sales Pipeline**

### Business Context
- **Key Highlights**, **Key Challenges**, **Funding Status**

## 🗄️ Database Schema

### FinancialMetrics Table
```sql
financial_metrics:
  - id (Primary Key)
  - company_id (Foreign Key to companies)
  - email_update_id (Foreign Key to email_updates)
  - reporting_period (e.g., "Q1 2025", "May 2025")
  - reporting_date (Date metrics are for)
  - extracted_date (When extraction occurred)
  - [25+ metric columns as strings to preserve formatting]
  - source_type ('email' or 'attachment')
  - source_file (filename if from attachment)
  - extraction_confidence ('high', 'medium', 'low')
  - extraction_notes
```

### MetricExtractions Table
```sql
metric_extractions:
  - id (Primary Key)
  - email_update_id (Foreign Key)
  - attachment_id (Foreign Key, nullable)
  - extracted_at (Timestamp)
  - extraction_method ('claude_ai', 'regex', 'manual')
  - extraction_status ('success', 'partial', 'failed')
  - raw_extraction (Raw extracted text)
  - error_message (If extraction failed)
  - retry_count
```

## 🚀 Quick Start

### 1. Check Current Statistics
```bash
# Show current financial metrics in database
./process_financials.sh --stats
```

### 2. Process Recent Emails
```bash
# Process emails from last 7 days
./process_financials.sh --days 7

# Dry run to see what would be processed
./process_financials.sh --days 7 --dry-run
```

### 3. Process Specific Company
```bash
# Process all emails for Validic
./process_financials.sh --company "Validic"

# Dry run for specific company
./process_financials.sh --company "Validic" --dry-run
```

### 4. Export Data
```bash
# Export all metrics to CSV
./process_financials.sh --export

# Export to specific file
./process_financials.sh --export my_metrics.csv
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- Anthropic API key for Claude
- SQLite database with email collection system

### Environment Setup
1. **Create `.env` file** with required variables:
```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
# ... other environment variables
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify database tables exist**:
```bash
python -c "from database.connection import SessionLocal; from database.financial_models import FinancialMetrics; print('✅ Financial metrics tables ready')"
```

## 📋 Command Line Usage

### Python Script (Direct)
```bash
# Show help
python process_financial_metrics.py --help

# Basic processing
python process_financial_metrics.py --days 30
python process_financial_metrics.py --email-id 123
python process_financial_metrics.py --company "Company Name"

# Options
python process_financial_metrics.py --dry-run --days 14
python process_financial_metrics.py --stats
python process_financial_metrics.py --export metrics.csv
```

### Shell Wrapper (Recommended)
```bash
# Show help
./process_financials.sh --help

# Basic commands
./process_financials.sh --stats
./process_financials.sh --days 7
./process_financials.sh --company "Validic"
./process_financials.sh --export

# Advanced usage
./process_financials.sh --dry-run --days 14
./process_financials.sh --email-id 123
./process_financials.sh --export custom_export.csv
```

## 🔍 How It Works

### 1. Email Processing
- Connects to existing email collection database
- Identifies emails that haven't been processed for financial metrics
- Processes both email content and attachments

### 2. Content Extraction
- **PDF Files**: Extracts text using PyPDF2
- **Excel Files**: Reads all sheets, converts to text representation
- **PowerPoint**: Extracts text from all slides and shapes
- **Email Content**: Uses raw email body text

### 3. AI Analysis
- Sends extracted content to Claude Sonnet 4
- Uses structured prompt to identify financial metrics
- Returns JSON with standardized metric fields
- Preserves original formatting (e.g., "$1.2M", "~$8.000M")

### 4. Data Storage
- Saves metrics to `financial_metrics` table
- Links to original email and company records
- Tracks extraction metadata and confidence
- Prevents duplicate processing

### 5. Quality Control
- **Confidence Scoring**: AI rates extraction confidence (high/medium/low)
- **Duplicate Prevention**: Won't reprocess already-analyzed emails
- **Error Handling**: Tracks failed extractions for review
- **Source Tracking**: Records whether metrics came from email or attachment

## 📈 Data Analysis Examples

### SQL Queries
```sql
-- Companies with highest ARR
SELECT company_name, arr, reporting_period 
FROM financial_metrics fm
JOIN companies c ON fm.company_id = c.id
WHERE arr != 'N/A' AND arr IS NOT NULL
ORDER BY CAST(REPLACE(REPLACE(arr, '$', ''), 'M', '') AS FLOAT) DESC;

-- Growth trends
SELECT company_name, reporting_period, arr_growth, mrr_growth
FROM financial_metrics fm
JOIN companies c ON fm.company_id = c.id
WHERE (arr_growth != 'N/A' OR mrr_growth != 'N/A')
ORDER BY company_name, reporting_date;

-- Cash runway analysis
SELECT company_name, cash_balance, runway_months, reporting_period
FROM financial_metrics fm
JOIN companies c ON fm.company_id = c.id
WHERE runway_months != 'N/A' AND runway_months IS NOT NULL
ORDER BY CAST(REPLACE(runway_months, ' months', '') AS INTEGER);
```

### Python Analysis
```python
from database.connection import SessionLocal
from database.models import Company
from database.financial_models import FinancialMetrics
import pandas as pd

# Export to pandas for analysis
session = SessionLocal()
query = session.query(FinancialMetrics).join(Company)
df = pd.read_sql(query.statement, session.bind)

# Analyze ARR distribution
arr_data = df[df['arr'] != 'N/A']['arr'].str.replace('$', '').str.replace('M', '').astype(float)
print(f"Average ARR: ${arr_data.mean():.1f}M")
print(f"Median ARR: ${arr_data.median():.1f}M")
```

## 🔧 Configuration

### Claude AI Settings
- **Model**: claude-sonnet-4-20250514
- **Max Tokens**: 2000 for responses
- **Content Limit**: 8000 characters per analysis
- **Retry Logic**: Built-in error handling

### File Type Support
- **PDF**: ✅ Full text extraction
- **Excel** (.xlsx, .xls): ✅ All sheets, formatted output
- **PowerPoint** (.pptx, .ppt): ✅ All slides and text shapes
- **Word**: ❌ Not yet supported
- **Images**: ❌ Not yet supported (OCR could be added)

### Performance
- **Processing Speed**: ~10-15 seconds per email with attachments
- **Batch Processing**: Handles multiple emails sequentially
- **Memory Usage**: Optimized for large Excel files
- **Error Recovery**: Continues processing if individual files fail

## 📊 Current Status

### Database Statistics (as of latest run)
- **Total Metrics Records**: 34
- **Companies with Metrics**: Multiple portfolio companies
- **Extraction Sources**: Email content + PDF/Excel/PowerPoint attachments
- **Average Confidence**: High (Claude performs well on financial data)

### Successfully Processed Companies
Examples include:
- **Validic**: ARR data, financial packages
- **Sift Media**: Financial presentations
- **CompostNow**: Multiple financial documents
- **Natryx**: Financial reports

## 🚨 Important Notes

### Data Accuracy
- **AI Limitations**: Claude is highly accurate but not perfect
- **Confidence Scores**: Always check low-confidence extractions
- **Original Formatting**: Preserved to maintain context (e.g., "~$8.000M")
- **Manual Review**: Recommended for critical business decisions

### Security
- **API Keys**: Store securely in `.env` file
- **Database**: Contains sensitive financial information
- **Attachments**: Stored locally, ensure proper access controls

### Maintenance
- **Regular Processing**: Run weekly/monthly to keep data current
- **Error Monitoring**: Check failed extractions periodically
- **Database Cleanup**: Consider archiving old metrics if needed

## 🔮 Future Enhancements

### Planned Features
- **Trend Analysis**: Automated growth rate calculations
- **Alerting**: Notify on concerning metrics (low cash, high burn)
- **Dashboard**: Web interface for viewing metrics
- **OCR Support**: Extract metrics from image-based documents
- **Advanced Analytics**: Cohort analysis, benchmarking

### Integration Opportunities
- **CRM Systems**: Sync with portfolio management tools
- **Reporting**: Automated monthly/quarterly reports
- **Forecasting**: Predictive analytics on financial trends

## 🆘 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Fix: Ensure you're in the project root and virtual environment is activated
cd /path/to/email-alert
source .venv/bin/activate
```

**Claude API Errors**
```bash
# Fix: Check API key in .env file
echo $ANTHROPIC_API_KEY
```

**Database Errors**
```bash
# Fix: Verify database tables exist
sqlite3 tracker.db ".tables"
```

**No Metrics Extracted**
```bash
# Debug: Run with specific email ID to see detailed output
python process_financial_metrics.py --email-id 123
```

### Getting Help
1. Check the logs for detailed error messages
2. Run with `--dry-run` to see what would be processed
3. Use `--stats` to verify current database state
4. Check individual email processing with specific `--email-id`

---

## 📞 Support

For technical issues or questions about the Financial Metrics Extraction System, please review the troubleshooting section above or check the main project documentation. 