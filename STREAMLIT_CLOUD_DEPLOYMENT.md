# Streamlit Community Cloud Deployment Guide

This guide explains how to deploy the Tweener Fund Portfolio Intelligence dashboard to Streamlit Community Cloud.

## Prerequisites

1. GitHub account with the repository
2. Streamlit Community Cloud account (free at https://streamlit.io/cloud)

## Project Structure

The project is organized for Streamlit Cloud deployment:

```
email-alert/
├── streamlit_app.py          # Main app entry point (REQUIRED in root)
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml          # App configuration
│   └── secrets.toml         # Secrets (create from example)
├── dashboard/               # Dashboard modules
├── auth/                    # Authentication system
├── database/                # Database models
└── pipeline/               # Email processing pipeline
```

## Deployment Steps

### 1. Prepare Secrets

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your actual values:
   - Database credentials
   - API keys (Anthropic, Google)
   - Authentication credentials
3. **IMPORTANT**: Never commit `secrets.toml` to Git!

### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your repository: `ShupingR/tweener-portco-email-alert`
4. Branch: `main` (or your branch)
5. Main file path: `streamlit_app.py`
6. Click "Deploy"

### 4. Add Secrets in Streamlit Cloud

1. In your app settings, go to "Secrets"
2. Copy the content from your local `.streamlit/secrets.toml`
3. Paste and save

## Configuration

### Environment Variables

Streamlit Cloud automatically sets:
- `STREAMLIT_SERVER_PORT`
- `STREAMLIT_SERVER_ADDRESS`

### Database Options

1. **PostgreSQL** (Recommended for production):
   ```toml
   [database]
   DATABASE_URL = "postgresql://user:password@host:5432/dbname"
   ```

2. **SQLite** (For testing only):
   ```toml
   [database]
   DATABASE_URL = "sqlite:///./email_tracker.db"
   ```

### Authentication

The app includes built-in authentication. Default admin credentials:
- Username: Set in `secrets.toml`
- Password: Set in `secrets.toml`

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `streamlit_app.py` is in the root directory
2. **Database Connection**: Check DATABASE_URL in secrets
3. **Missing Dependencies**: Update `requirements.txt`
4. **Memory Issues**: Streamlit Cloud has memory limits; optimize data processing

### Logs

View logs in Streamlit Cloud dashboard:
1. Go to your app
2. Click "Manage app"
3. View "Logs"

## Features

- **Authentication**: Session-based login system
- **Dashboard**: Portfolio companies overview
- **Financial Metrics**: Automated extraction and display
- **Portfolio Assistant**: AI-powered analysis
- **Email Processing**: Automated email collection (requires setup)

## Security Notes

1. Use strong passwords in production
2. Rotate API keys regularly
3. Use PostgreSQL with SSL in production
4. Keep secrets.toml out of version control

## Support

For issues or questions:
- GitHub Issues: https://github.com/ShupingR/tweener-portco-email-alert/issues
- Streamlit Forums: https://discuss.streamlit.io/