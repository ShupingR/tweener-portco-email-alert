# 🔐 Tweener Insights Dashboard

A comprehensive portfolio intelligence dashboard for Tweener Fund with secure authentication, financial metrics tracking, and AI-powered portfolio analysis.

## 📁 Project Structure

```
email-alert/
├── auth/                    # Authentication system
│   ├── __init__.py
│   ├── auth_config.py      # Authentication configuration
│   ├── auth_utils.py       # Session management utilities
│   ├── login_page.py       # Login interface component
│   ├── manage_users.py     # User management CLI tool
│   ├── setup_auth.py       # Interactive setup script
│   └── users.json          # User credentials (hashed)
├── dashboard/              # Main dashboard application
│   ├── streamlit_app.py    # Main Streamlit entry point
│   ├── Tweener_Insights.py # Main dashboard functionality
│   ├── pages/              # Dashboard pages
│   └── design/             # UI assets and styling
├── scripts/deployment/     # Deployment configurations
│   └── deploy.sh          # Unified deployment script
├── docs/                  # Documentation
│   ├── README.md         # Main documentation
│   ├── SECURITY_GUIDE.md # Security documentation
│   ├── DEPLOYMENT_GUIDE.md # Deployment guide
│   └── *.md              # Other documentation
├── scripts/               # Utility scripts
│   ├── refresh_dashboard.py
│   └── test_logo.py
├── database/              # Database models and connections
├── pipeline/              # Email processing pipeline
├── integrations/          # External service integrations
├── utils/                 # Utility functions
├── alerts/                # Alert system
├── setup/                 # Initial setup scripts
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Setup Authentication
```bash
# Interactive setup (recommended)
python auth/setup_auth.py

# Or manual setup
python auth/manage_users.py add admin tweenerfund
```

**Quick Authentication Setup:**
- **Default Users:** admin, scot, robbie, nikita, shuping, link, derek
- **Default Password:** `tweenerfund` (change immediately!)
- **User Management:** `python auth/manage_users.py list/add/remove/change`
- **Session Timeout:** 8 hours
- **Security:** SHA-256 password hashing, secure session tokens

### 2. Start Dashboard
```bash
streamlit run dashboard/streamlit_app.py --server.port 8501
```

### 3. Access Dashboard
- **URL:** http://localhost:8501
- **Login:** Use credentials created in step 1

## 🔐 Authentication

### Default Users
- **admin** / `tweenerfund`
- **scot** / `tweenerfund`
- **robbie** / `tweenerfund`
- **nikita** / `tweenerfund`
- **shuping** / `tweenerfund`
- **link** / `tweenerfund`
- **derek** / `tweenerfund`

### User Management
```bash
# List all users
python auth/manage_users.py list

# Add new user
python auth/manage_users.py add username password

# Remove user
python auth/manage_users.py remove username

# Change password
python auth/manage_users.py change username new_password
```

## 📊 Features

- **🔐 Secure Authentication** - Session-based login with password hashing
- **📈 Financial Metrics** - ARR, MRR, growth rates, cash balances
- **🤖 AI Portfolio Assistant** - Natural language queries about portfolio data
- **📧 Email Integration** - Automatic email processing and data extraction
- **📊 Interactive Dashboards** - Real-time portfolio visualization
- **🔔 Alert System** - Automated notifications for important metrics
- **☁️ Cloud Deployment** - Ready for Streamlit Community Cloud deployment

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

## 📚 Documentation

- **[Security Guide](docs/SECURITY_GUIDE.md)** - Authentication and security best practices
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
# Deploy to Streamlit Community Cloud
# Follow instructions in STREAMLIT_CLOUD_DEPLOYMENT.md

# Local deployment
bash scripts/deployment/deploy.sh --local
```

## 🏗️ Architecture

### Core Components
- **Authentication System** - Secure user management and session handling
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

## 🔒 Security Features

- **Password Hashing** - SHA-256 with salt
- **Session Management** - Secure tokens with timeout
- **Environment Variables** - Secure credential storage
- **HTTPS Support** - Production-ready SSL configuration
- **Access Control** - User-based permissions

## 🚀 Deployment

### Local Development
```bash
streamlit run dashboard/streamlit_app.py --server.port 8501
```

### Streamlit Community Cloud
```bash
# Deploy to Streamlit Community Cloud
# Follow instructions in STREAMLIT_CLOUD_DEPLOYMENT.md
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
- Review the security guide for authentication issues
- Contact the development team

---

**Tweener Insights Dashboard** - Portfolio Intelligence with AI-Powered Analysis 