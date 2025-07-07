# Tweener Fund Portfolio Intelligence Platform

A comprehensive portfolio management and financial analysis platform that processes email updates from portfolio companies, extracts financial metrics, and provides AI-powered insights through an interactive dashboard.

## 🚀 Quick Start

### 1. Setup Authentication
```bash
# Interactive setup (recommended)
python auth/setup_auth.py

# Or manual setup
python auth/manage_users.py add admin TweenerAdmin2025
```

**Unified Credentials (Local & Production):**
- **admin** / `TweenerAdmin2025` - Full access to all features
- **viewer** / `ViewerAccess2025` - Read-only access to dashboard
- **analyst** / `AnalystAccess2025` - Can view and create reports

### 2. Start Dashboard
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 3. Access Dashboard
- **URL:** http://localhost:8501
- **Login:** Use credentials listed above

## 📊 Features

- **🔐 Secure Authentication** - Session-based login with password hashing
- **📈 Financial Metrics** - ARR, MRR, growth rates, cash balances
- **🤖 AI Portfolio Assistant** - Natural language queries about portfolio data
- **📧 Email Integration** - Automatic email processing and data extraction
- **📊 Interactive Dashboards** - Real-time portfolio visualization
- **🔔 Alert System** - Automated notifications for important metrics
- **☁️ Cloud Deployment** - Ready for Google Cloud Run deployment

## 🏗️ Architecture

### Core Components
- **Authentication System** - Secure user management and session handling
- **Dashboard Engine** - Streamlit-based interactive interface
- **Data Pipeline** - Email processing and financial metrics extraction
- **Database Layer** - SQLAlchemy ORM with SQLite
- **AI Integration** - Claude API for natural language processing
- **Alert System** - Automated monitoring and notifications

### Data Flow
1. **Email Collection** → Gmail API integration
2. **Data Processing** → Financial metrics extraction
3. **Database Storage** → SQLAlchemy ORM
4. **Dashboard Display** → Streamlit interface
5. **User Interaction** → AI-powered portfolio assistant

## 🛠️ Development

### Prerequisites
- Python 3.8+
- SQLite database
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
# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Gmail Integration
GMAIL_USERNAME=your_email@gmail.com
GMAIL_PASSWORD=your_app_password

# Database
DATABASE_URL=sqlite:///tracker.db

# API Keys
ANTHROPIC_API_KEY=your_claude_api_key
```

## 📁 Project Structure

```
email-alert/
├── streamlit_app.py              # Main Streamlit application
├── pages/                        # Streamlit multipage files
│   ├── 1_📊_Tweener_Insights.py  # Main dashboard
│   └── 2_🤖_Portfolio_Assistant.py # AI chatbot
├── deployment/                   # Google Cloud deployment files
│   ├── Dockerfile               # Container configuration
│   ├── cloudbuild.yaml          # CI/CD pipeline
│   ├── deploy-gcp.sh            # Deployment script
│   ├── .gcloudignore            # Upload exclusions
│   └── .dockerignore            # Docker exclusions
├── database/                     # Database models and connection
├── pipeline/                     # Email processing pipeline
├── integrations/                 # External API integrations
├── utils/                        # Utility functions
├── auth/                         # Authentication system
├── alerts/                       # Alert system
├── setup/                        # Initial setup scripts
├── scripts/                      # Maintenance scripts
├── .streamlit/                   # Streamlit configuration
├── requirements.txt              # Python dependencies
└── env.example                   # Environment template
```

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Google Cloud Run
```bash
# Deploy to Google Cloud
bash deployment/deploy-gcp.sh
```

### Docker
```bash
# Build and run locally
docker build -f deployment/Dockerfile -t tweener-dashboard .
docker run -p 8501:8501 tweener-dashboard
```

## 🔧 Scripts

### Dashboard Management
```bash
# Refresh dashboard data
python scripts/refresh_dashboard.py

# Test logo display
python scripts/test_logo.py
```

### Email Processing
```bash
# Collect emails from Gmail
python -m pipeline.email_collector --days=7

# Process financial metrics
python process_financial_metrics.py --stats
```

## 🔒 Security Features

- **Password Hashing** - SHA-256 with salt
- **Session Management** - Secure tokens with timeout
- **Environment Variables** - Secure credential storage
- **HTTPS Support** - Production-ready SSL configuration
- **Access Control** - User-based permissions

## 📚 Documentation

- **[Financial Metrics](docs/FINANCIAL_METRICS_README.md)** - Financial data processing and metrics
- **[Daily Usage](docs/DAILY_USAGE.md)** - Daily operational procedures
- **[Security Guide](docs/SECURITY_GUIDE.md)** - Authentication and security best practices
- **[Dashboard Guide](docs/DASHBOARD_README.md)** - Dashboard usage and features

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
- Review the security guide for authentication issues
- Contact the development team

---

**Tweener Insights Dashboard** - Portfolio Intelligence with AI-Powered Analysis 