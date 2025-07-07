#!/usr/bin/env python3
"""
Tweener Fund Portfolio Dashboard - Landing Page

Welcome to the Tweener Fund Portfolio Intelligence Platform.
This is the main entry point for the Streamlit dashboard.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import enhanced authentication with error handling
try:
    from auth import show_login_page, check_authentication, show_user_info, get_current_user, check_permission
    AUTH_AVAILABLE = True
except ImportError as e:
    st.error(f"Authentication module import error: {e}")
    AUTH_AVAILABLE = False

# Import database initialization
try:
    from database.connection import init_db
    from database.models import Base
    from database.financial_models import FinancialMetrics, MetricExtraction
    DB_AVAILABLE = True
except ImportError as e:
    st.error(f"Database module import error: {e}")
    DB_AVAILABLE = False

# Import automated email processing
try:
    from scripts.automated_email_processor import AutomatedEmailProcessor
    EMAIL_PROCESSOR_AVAILABLE = True
except ImportError as e:
    st.error(f"Email processor module import error: {e}")
    EMAIL_PROCESSOR_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Tweener Fund - Portfolio Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tweener Fund Brand Colors - Custom CSS
st.markdown("""
<style>
    /* Tweener Fund Brand Theme */
    :root {
        --tweener-primary: #4fd1c7;
        --tweener-secondary: #38b2ac;
        --tweener-accent: #81e6d9;
        --tweener-dark-green: #2d5016;
        --tweener-orange: #ed8936;
    }
    
    .stApp {
        background-color: #f7fafc !important;
        color: #2d3748 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    h1 {
        color: var(--tweener-primary) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--tweener-primary) !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    .main > div {
        padding-top: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize database on startup
    if DB_AVAILABLE:
        try:
            init_db()
            st.success("✅ Database initialized successfully")
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    # Check for automated email processing requests
    if EMAIL_PROCESSOR_AVAILABLE:
        # Check if this is an API call for email processing
        if st.experimental_get_query_params().get("action") == ["process_emails"]:
            st.set_page_config(page_title="Email Processing", layout="wide")
            run_email_processing()
            return
    
    # Check if authentication is available
    if not AUTH_AVAILABLE:
        st.error("Authentication system not available. Please install required dependencies.")
        st.info("For local development, install: pip install google-cloud-secret-manager")
        return
    
    # Check authentication first
    if not check_authentication():
        show_login_page()
        return
    
    # Show user info in sidebar
    show_user_info()
    
    # Get current user for personalization
    current_user = get_current_user()
    
    # Header with Tweener Fund branding
    st.title("💰 Tweener Insights")
    st.markdown("**Generative AI-Powered Portfolio Management Platform**")
    
    st.markdown("---")
    
    # Welcome section with personalization
    if current_user:
        welcome_name = current_user.get('full_name', 'User')
        user_role = current_user.get('role', 'user').title()
        st.header(f"🎯 Welcome, {welcome_name}!")
        st.markdown(f"**Role:** {user_role} | **Access Level:** {current_user.get('role', 'N/A')}")
    else:
        st.header("🎯 Welcome to Your Portfolio Command Center")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Tweener Fund's Portfolio Intelligence Platform** provides real-time insights, 
        financial analytics, and AI-powered portfolio management tools to help you 
        make informed investment decisions.
        
        ### 🚀 What You Can Do:
        - **📊 View Financial Metrics** - Real-time portfolio performance and KPIs
        - **📈 Analyze Growth Trends** - Revenue, customer, and operational metrics
        - **🤖 AI Portfolio Assistant** - Get instant answers about your portfolio
        - **📋 Track Company Updates** - Monitor portfolio company progress
        - **💰 Cash & Runway Analysis** - Financial health monitoring
        """)
    
    with col2:
        st.markdown("""
        ### 📱 Quick Navigation
        
        Use the sidebar to navigate between:
        
        **📊 Tweener Insights** - Main dashboard with financial metrics
        
        **🤖 Portfolio Assistant** - AI chatbot for portfolio analysis
        """)
    
    st.markdown("---")
    
    # Key Features
    st.header("🔧 Platform Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 **Financial Analytics**
        - ARR/MRR tracking
        - Growth rate analysis
        - Cash runway monitoring
        - Customer metrics
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 **AI Assistant**
        - Natural language queries
        - Portfolio insights
        - Data interpretation
        - Trend analysis
        """)
    
    with col3:
        st.markdown("""
        ### 📈 **Real-time Data**
        - Live portfolio updates
        - Email integration
        - Automated metrics
        - Performance tracking
        """)
    
    st.markdown("---")
    
    # Role-based feature access
    st.markdown("---")
    st.header("🔑 Your Access Level")
    
    if check_permission("read"):
        st.success("✅ **Read Access** - View dashboard and portfolio data")
    
    if check_permission("write"):
        st.success("✅ **Write Access** - Create and edit reports")
    
    if check_permission("user_management"):
        st.success("✅ **Admin Access** - Manage users and settings")
        
        # Admin section
        with st.expander("🔧 Admin Controls", expanded=False):
            st.markdown("""
            **Admin Features Available:**
            - User management
            - System settings
            - Email configuration
            - Security settings
            """)
    
    # Getting Started
    st.header("🚀 Getting Started")
    
    st.markdown("""
    1. **📊 View Dashboard** - Access your portfolio metrics based on your role
    2. **🤖 Ask Questions** - Use the AI assistant for portfolio insights
    3. **📋 Explore Data** - Analyze portfolio companies (permissions apply)
    4. **📈 Track Performance** - Monitor key financial indicators
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #718096; font-size: 0.9rem;'>
        <strong>Tweener Fund Portfolio Intelligence Platform</strong><br>
        Powered by Streamlit & AI • Secure • Real-time
    </div>
    """, unsafe_allow_html=True)

def run_email_processing():
    """Run automated email processing for Cloud Scheduler"""
    st.title("🤖 Automated Email Processing")
    st.markdown("**Processing emails and extracting financial metrics...**")
    
    try:
        # Get parameters from query string
        params = st.experimental_get_query_params()
        days = int(params.get("days", ["7"])[0])
        dry_run = params.get("dry_run", ["false"])[0].lower() == "true"
        
        st.info(f"📧 Processing emails from last {days} days")
        if dry_run:
            st.warning("🧪 Running in DRY RUN mode - no changes will be made")
        
        # Initialize processor
        with st.spinner("Initializing email processor..."):
            processor = AutomatedEmailProcessor(dry_run=dry_run)
        
        # Run processing
        with st.spinner("Processing emails and extracting metrics..."):
            success = processor.run_full_processing(days_back=days)
        
        if success:
            st.success("✅ Email processing completed successfully!")
            st.balloons()
        else:
            st.error("❌ Email processing failed")
            
    except Exception as e:
        st.error(f"❌ Error during email processing: {e}")
        st.exception(e)

if __name__ == "__main__":
    main() 