# Streamlit Community Cloud Deployment Guide

## 🚀 **Deployment Steps**

### **1. Prepare Your Repository**

✅ **Already Done:**
- ✅ Single entry point: `streamlit_app.py`
- ✅ Updated `requirements.txt` with compatible versions
- ✅ Created `packages.txt` for system dependencies
- ✅ Updated `.streamlit/config.toml` for cloud settings
- ✅ Template `.streamlit/secrets.toml` created

### **2. Deploy to Streamlit Community Cloud**

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure your app:**
   - **Repository**: `your-username/email-alert`
   - **Branch**: `main` (or your preferred branch)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: `tweener-fund-portfolio` (or your preferred name)

### **3. Configure Secrets**

In the Streamlit Cloud dashboard, go to **Settings → Secrets** and add:

```toml
[database]
DATABASE_URL = "sqlite:///./email_tracker.db"

[auth]
SESSION_SECRET_KEY = "your-actual-secret-key-here"
ADMIN_USERNAME = "your-admin-username"
ADMIN_PASSWORD = "your-secure-password"

[email]
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"

[api_keys]
ANTHROPIC_API_KEY = "your-anthropic-api-key"

[app]
APP_NAME = "Tweener Fund Portfolio Intelligence"
COMPANY_NAME = "Tweener Fund"
SUPPORT_EMAIL = "support@tweenerfund.com"
```

### **4. Important Notes**

#### **Database Considerations:**
- **SQLite**: Works but data is ephemeral (resets on restart)
- **PostgreSQL**: Recommended for production (persistent data)
- **Free tier**: Limited to SQLite or external PostgreSQL

#### **File Storage:**
- **Attachments**: Stored locally (ephemeral)
- **Consider**: Cloud storage (S3, Google Cloud) for persistent files

#### **Email Processing:**
- **Gmail API**: Requires proper OAuth setup
- **App passwords**: Work for basic IMAP access
- **Rate limits**: Be mindful of API quotas

### **5. Environment Variables**

Streamlit Cloud automatically reads from `.streamlit/secrets.toml` or the secrets configuration in the dashboard.

### **6. Troubleshooting**

#### **Common Issues:**
1. **Import errors**: Check `requirements.txt` versions
2. **Database errors**: Ensure SQLite file path is correct
3. **Authentication issues**: Verify secrets configuration
4. **File upload errors**: Check `maxUploadSize` in config

#### **Debug Mode:**
Add to your app for debugging:
```python
import streamlit as st
st.write("Debug: Secrets loaded successfully")
st.write(st.secrets)
```

### **7. Production Checklist**

- [ ] All secrets configured in Streamlit Cloud
- [ ] Database connection tested
- [ ] Email collection working
- [ ] File uploads functional
- [ ] Authentication working
- [ ] Error handling in place
- [ ] Performance optimized

### **8. Security Best Practices**

1. **Never commit secrets to Git**
2. **Use strong passwords**
3. **Rotate API keys regularly**
4. **Monitor usage and logs**
5. **Backup data regularly**

## 🎯 **Next Steps**

1. **Deploy to Streamlit Cloud**
2. **Test all functionality**
3. **Configure monitoring**
4. **Set up backups**
5. **Document user access**

Your app will be available at: `https://your-app-name.streamlit.app`