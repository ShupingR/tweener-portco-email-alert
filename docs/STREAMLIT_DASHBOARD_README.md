# 💰 Streamlit Financial Metrics Dashboard

An interactive web dashboard built with Streamlit for visualizing and analyzing portfolio company financial metrics. Features real-time charts, filtering, and data exploration capabilities.

## 🚀 Quick Start

### Start the Dashboard
```bash
# Using the launcher script (recommended)
./start_streamlit_dashboard.sh

# Or run directly
streamlit run dashboard/streamlit_app.py --server.port=8501
```

### Access the Dashboard
The dashboard will automatically open in your browser at: **http://localhost:8501**

## ✨ Key Features

### 📊 **Interactive Visualizations**
- **ARR Comparison Chart**: Horizontal bar chart showing Annual Recurring Revenue by company
- **Growth Analysis**: Color-coded growth rate visualization (green=positive, red=negative)
- **Cash vs Runway Scatter Plot**: Interactive plot showing financial health positioning

### 🔍 **Advanced Filtering**
- **Company Filter**: Focus on specific portfolio companies
- **Confidence Level**: Filter by AI extraction confidence (High/Medium/Low)
- **Data Source**: Separate email vs attachment-derived metrics
- **Date Range**: Analyze metrics from specific time periods

### 📈 **Real-time Analytics**
- **Portfolio Overview**: Key statistics with metric cards
- **Company Summary**: Latest metrics for each company
- **Search Functionality**: Real-time text search across all data
- **CSV Export**: Download filtered data for external analysis

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tabbed Interface**: Organized sections for different analysis types
- **Interactive Charts**: Hover, zoom, and pan capabilities with Plotly
- **Auto-refresh**: Data updates every 5 minutes via caching

## 📊 Dashboard Sections

### 1. Portfolio Overview (Top Section)
```
📊 Portfolio Overview
┌─────────────┬─────────────┬─────────────┬─────────────┐
│Total Metrics│Companies    │Portfolio    │Recent       │
│     34      │Tracked 19/151│Coverage 12.6%│Updates 34   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### 2. Interactive Filters (Sidebar)
- **🔍 Filters**
  - Select Company: All | CompostNow | Validic | Tromml...
  - Confidence Level: All | High | Medium | Low
  - Data Source: All | Email | Attachment
  - Date Range: Interactive date picker

### 3. Financial Analysis (Tabbed Charts)
- **💰 Revenue Metrics**: ARR comparison across companies
- **📊 Growth Analysis**: Growth rate visualization
- **💵 Cash & Runway**: Financial health scatter plot

### 4. Company Summary Table
Interactive table showing latest metrics for each company:
- Company name and last update date
- Key financial metrics (ARR, MRR, Cash, Runway)
- Growth indicators and confidence levels
- Number of records per company

### 5. Detailed Data Table
Comprehensive searchable table with:
- All financial metrics and metadata
- Real-time search functionality
- CSV download capability
- Responsive column layout

## 🎯 Use Cases

### 1. **Portfolio Monitoring**
- Quick overview of all companies' financial health
- Identify companies needing attention (low cash, negative growth)
- Track portfolio-wide metrics and trends

### 2. **Company Deep Dive**
- Filter by specific company to see all historical data
- Analyze growth trends and financial trajectory
- Review data quality and extraction confidence

### 3. **Data Quality Review**
- Filter by confidence level to find metrics needing review
- Compare email vs attachment-derived data
- Identify companies with missing or outdated metrics

### 4. **Investment Analysis**
- Compare ARR across portfolio companies
- Analyze growth rates and financial health
- Export data for detailed financial modeling

## 🔧 Technical Features

### Data Processing
- **Real-time Loading**: Direct SQLite database connection
- **Smart Parsing**: Converts text values ("$1.2M") to numeric for charts
- **Error Handling**: Graceful handling of missing or invalid data
- **Caching**: 5-minute cache for improved performance

### Chart Types
- **Horizontal Bar Charts**: For ARR comparison
- **Colored Bar Charts**: For growth rate analysis
- **Scatter Plots**: For multi-dimensional analysis
- **Interactive Elements**: Hover tooltips, zoom, pan

### Data Export
- **CSV Download**: Filtered data export
- **Timestamped Files**: Automatic filename with date
- **Clean Formatting**: Processed data ready for analysis

## 📱 Responsive Design

### Desktop (Recommended)
- **Full Layout**: All features and charts visible
- **Wide Charts**: Optimal chart viewing experience
- **Sidebar Filters**: Easy access to all filtering options

### Tablet
- **Adaptive Layout**: Charts stack vertically
- **Touch-friendly**: All controls optimized for touch
- **Readable Text**: Appropriate font sizes

### Mobile
- **Mobile-first**: Streamlit's responsive design
- **Simplified Tables**: Horizontal scrolling for large tables
- **Collapsible Sidebar**: Space-efficient filtering

## 🚀 Performance

### Loading Speed
- **Fast Initial Load**: ~2-3 seconds for 34 records
- **Cached Data**: Subsequent loads under 1 second
- **Efficient Queries**: Optimized database queries

### Chart Rendering
- **Plotly Performance**: Hardware-accelerated rendering
- **Interactive Response**: Real-time chart updates
- **Large Dataset Support**: Handles hundreds of records

### Memory Usage
- **Efficient Caching**: Streamlit's built-in caching
- **Pandas Optimization**: Vectorized operations
- **Memory Management**: Automatic cleanup

## 🔄 Data Updates

### Automatic Refresh
- **Cache TTL**: 5-minute automatic refresh
- **Manual Refresh**: Browser refresh for immediate updates
- **Real-time Sync**: Always shows latest database state

### Processing New Data
```bash
# Extract new financial metrics
./process_financials.sh --days 7

# Dashboard automatically shows new data within 5 minutes
# Or refresh browser for immediate update
```

## 🎨 Customization

### Styling
- **Custom CSS**: Embedded styling for professional look
- **Color Schemes**: Consistent color palette
- **Typography**: Clean, readable fonts

### Charts
- **Color Coding**: Meaningful colors (green=good, red=concerning)
- **Formatting**: Currency and percentage formatting
- **Tooltips**: Detailed hover information

## 🔧 Advanced Features

### Search Functionality
```python
# Real-time search across all columns
search_term = st.text_input("🔍 Search metrics")
# Searches: company names, metrics, periods, highlights, etc.
```

### Data Filtering
```python
# Multiple filter combinations
filtered_df = df[
    (df['company_name'] == selected_company) &
    (df['confidence'] == selected_confidence) &
    (df['date'] >= start_date)
]
```

### Chart Interactions
- **Zoom**: Mouse wheel or touch gestures
- **Pan**: Click and drag to explore
- **Hover**: Detailed metric information
- **Select**: Click on chart elements

## 🛠️ Troubleshooting

### Common Issues

**Dashboard Won't Start**
```bash
# Check Streamlit installation
pip install streamlit plotly

# Verify database exists
ls -la tracker.db
```

**No Data Showing**
```bash
# Ensure financial metrics have been extracted
./process_financials.sh --stats

# Check database connection
python -c "from database.connection import SessionLocal; print('✅ Database OK')"
```

**Charts Not Displaying**
```bash
# Verify Plotly installation
pip install plotly

# Check browser compatibility (modern browsers required)
```

**Port Conflicts**
```bash
# Streamlit uses port 8501 by default
# Change port if needed:
streamlit run dashboard/streamlit_app.py --server.port=8502
```

## 🎯 Comparison: Streamlit vs Flask Dashboard

### Streamlit Advantages ✅
- **Interactive Charts**: Built-in Plotly integration
- **No HTML/CSS Required**: Pure Python development
- **Real-time Filtering**: Instant UI updates
- **Mobile Responsive**: Automatic responsive design
- **Data Exploration**: Built-in data manipulation widgets
- **Rapid Development**: Faster to build and modify

### Flask Advantages ✅
- **Custom Design**: Full control over HTML/CSS
- **Production Ready**: More suitable for production deployment
- **API Endpoints**: RESTful API capabilities
- **Lightweight**: Smaller footprint

### Recommendation 🎯
**Use Streamlit for:**
- Data analysis and exploration
- Internal dashboards
- Rapid prototyping
- Interactive visualizations

**Use Flask for:**
- Production web applications
- Custom user interfaces
- API services
- Public-facing dashboards

## 🚀 Future Enhancements

### Immediate Opportunities
- **Time Series Charts**: Track metrics over time
- **Cohort Analysis**: Group companies by investment vintage
- **Benchmark Comparisons**: Industry standard comparisons
- **Alert Notifications**: Real-time alerts for concerning metrics

### Advanced Features
- **Machine Learning**: Predictive analytics and forecasting
- **Portfolio Optimization**: Investment recommendation engine
- **Automated Reporting**: Scheduled PDF/email reports
- **Integration APIs**: Connect with external portfolio tools

---

## 📞 Quick Reference

**🌐 Dashboard URL**: http://localhost:8501  
**🚀 Start Command**: `./start_streamlit_dashboard.sh`  
**📊 Current Data**: 34 metrics from 19 companies  
**🔄 Auto-refresh**: Every 5 minutes  
**📱 Compatibility**: All modern browsers, mobile-friendly  

**Status**: ✅ Running and operational with interactive charts and real-time filtering! 