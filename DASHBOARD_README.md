# 💰 Financial Metrics Dashboard

A web-based dashboard for viewing portfolio company financial metrics extracted from email updates and attachments.

## 🚀 Quick Start

### Start the Dashboard
```bash
# Using the launcher script (recommended)
./start_dashboard.sh

# Or run directly
python dashboard/app.py
```

### Access the Dashboard
Open your web browser and go to: **http://localhost:8888**

## 📊 Dashboard Features

### Overview Statistics
- **Total Metrics**: Number of financial records extracted
- **Companies Tracked**: Portfolio companies with financial data
- **Portfolio Coverage**: Percentage of companies with metrics
- **Recent Updates**: Metrics extracted in the last 30 days

### Company Summary
- Grid view of all companies with financial metrics
- Shows number of records per company
- Displays last update date for each company

### Financial Metrics Table
- **Search Functionality**: Filter by company name, metrics, or reporting period
- **Key Metrics Display**: ARR, MRR, Cash Balance, Runway, Growth rates
- **Source Tracking**: Shows if data came from email or attachment
- **Confidence Indicators**: AI extraction confidence levels (High/Medium/Low)
- **Auto-refresh**: Updates every 5 minutes

## 🎨 Dashboard Sections

### 1. Statistics Cards
Shows key portfolio metrics at a glance:
- 34 total metrics records
- 19 companies tracked (12.6% coverage)
- All recent updates from last 30 days

### 2. Company Grid
Visual overview of companies with data:
- **CompostNow**: 6 records
- **Validic**: 4 records  
- **Tromml**: 3 records
- **Sift Media**: 3 records
- **Natryx**: 3 records

### 3. Metrics Table
Detailed financial data with columns:
- Company name and reporting period
- Revenue metrics (ARR, MRR)
- Financial health (Cash, Runway)
- Growth indicators
- Data source and confidence

## 🔍 Using the Dashboard

### Search and Filter
- Use the search box to find specific companies or metrics
- Search works across all table columns
- Real-time filtering as you type

### Understanding Confidence Levels
- **🟢 High**: Clear, well-structured financial data
- **🟡 Medium**: Some ambiguity but reliable metrics
- **🔴 Low**: Unclear or incomplete data (review recommended)

### Data Sources
- **📧 Email**: Metrics extracted from email content
- **📎 Attachment**: Metrics from PDF, Excel, or PowerPoint files

## 🔧 Technical Details

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite with financial metrics tables
- **Styling**: Modern CSS with responsive design

### API Endpoints
- `GET /`: Main dashboard page
- `GET /api/metrics`: JSON API for all metrics
- `GET /api/company/<name>`: JSON API for specific company

### Auto-refresh
Dashboard automatically refreshes every 5 minutes to show latest data.

## 🛠️ Maintenance

### Updating Data
The dashboard shows real-time data from the database. To update:
```bash
# Process recent emails for new metrics
./process_financials.sh --days 7

# The dashboard will automatically show new data
```

### Stopping the Dashboard
Press `Ctrl+C` in the terminal where the dashboard is running.

### Troubleshooting
- **Port conflicts**: Dashboard uses port 8888 (changed from 5000/8080 due to conflicts)
- **No data showing**: Ensure financial metrics have been extracted
- **Dashboard not loading**: Check that Flask is installed and database exists

## 🎯 Next Steps

### Immediate Use
1. **Monitor regularly**: Check dashboard weekly for new metrics
2. **Review low confidence**: Manually verify low-confidence extractions
3. **Track trends**: Watch for growth patterns and concerning metrics

### Future Enhancements
- **Charts and graphs**: Visual trend analysis
- **Alerts**: Notifications for concerning metrics
- **Export features**: Download filtered data
- **Company deep-dive**: Individual company pages

---

**Dashboard URL**: http://localhost:8888  
**Status**: ✅ Running and operational  
**Data**: 34 metrics from 19 companies 