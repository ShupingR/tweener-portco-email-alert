# Tweener Insights - Portfolio Intelligence Dashboard

A comprehensive financial dashboard for tracking portfolio company metrics, powered by AI-driven data extraction and analysis.

## 📁 Project Structure

```
email-alert/
├── dashboard/             # Streamlit dashboard application
│   ├── streamlit_app.py   # Main dashboard entry point
│   ├── Tweener_Insights.py # Core dashboard functionality
│   └── design/            # UI assets and styling
├── database/              # Database models and connection
├── pipeline/              # Email processing and data extraction
├── integrations/          # External API integrations
├── alerts/                # Alert system and notifications
├── scripts/               # Utility scripts and automation
├── deployment/            # Cloud deployment configurations
├── docs/                  # Documentation
├── setup/                 # Initial setup scripts
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Start Dashboard
```bash
streamlit run dashboard/streamlit_app.py --server.port 8501
```

### 2. Access Dashboard
- **URL:** http://localhost:8501
- **No login required** - Dashboard is accessible directly

## 📊 Features

- **📈 Financial Metrics** - ARR, MRR, growth rates, cash balances
- **🤖 AI Portfolio Assistant** - Natural language queries about portfolio data
- **📧 Email Integration** - Automatic email processing and data extraction
- **📊 Interactive Dashboards** - Real-time portfolio visualization
- **🔔 Alert System** - Automated notifications for important metrics
- **☁️ Cloud Deployment** - Ready for Google Cloud Platform deployment

## 🛠️ Development

### Prerequisites
- Python 3.8+
- SQLite (or PostgreSQL for production)
- Gmail API credentials (for email integration)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd email-alert

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env with your credentials
```

### Environment Variables
```bash
# Gmail Integration
GMAIL_USERNAME=your_email@gmail.com
GMAIL_PASSWORD=your_app_password

# Database
DATABASE_URL=sqlite:///tracker.db

# API Keys
ANTHROPIC_API_KEY=your_claude_api_key
```

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Cloud deployment instructions
- **[Dashboard Guide](docs/DASHBOARD_README.md)** - Dashboard usage and features
- **[Financial Metrics](docs/FINANCIAL_METRICS_README.md)** - Financial data processing

## 🔧 Scripts

### Dashboard Management
```bash
# Refresh dashboard data
python scripts/refresh_dashboard.py

# Test logo display
python scripts/test_logo.py
```

### Deployment
```bash
# Quick deploy to Google Cloud
bash deployment/quick-deploy.sh

# Simple deploy (no Docker)
bash deployment/simple-deploy.sh
```

## 🏗️ Architecture

### Core Components
- **Dashboard Engine** - Streamlit-based interactive interface
- **Data Pipeline** - Email processing and financial metrics extraction
- **Database Layer** - SQLAlchemy ORM with SQLite/PostgreSQL
- **AI Integration** - Claude API for natural language processing
- **Alert System** - Automated monitoring and notifications

### Data Flow
1. **Email Collection** → Gmail API integration
2. **Data Processing** → Financial metrics extraction
3. **Database Storage** → SQLAlchemy ORM
4. **Dashboard Display** → Streamlit interface
5. **User Interaction** → AI-powered portfolio assistant

## 🚀 Deployment

### Local Development
```bash
streamlit run dashboard/streamlit_app.py --server.port 8501
```

### Google Cloud Platform
```bash
# Quick deployment
bash deployment/quick-deploy.sh

# Manual deployment
gcloud app deploy deployment/app.yaml
```

### Docker
```bash
# Build and run
docker build -f deployment/Dockerfile -t tweener-dashboard .
docker run -p 8501:8501 tweener-dashboard
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary to Tweener Fund.

## 🆘 Support

For technical support or questions:
- Check the documentation in `docs/` 