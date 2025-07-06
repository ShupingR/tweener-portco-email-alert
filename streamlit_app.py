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
    # Header with Tweener Fund branding
    st.title("💰 Tweener Fund Portfolio Intelligence")
    st.markdown("**Generative AI-Powered Portfolio Management Platform**")
    
    st.markdown("---")
    
    # Welcome section
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
    
    # Getting Started
    st.header("🚀 Getting Started")
    
    st.markdown("""
    1. **📊 View Dashboard** - Click on "Tweener Insights" in the sidebar to see your portfolio metrics
    2. **🤖 Ask Questions** - Use the "Portfolio Assistant" to get AI-powered insights
    3. **📋 Explore Data** - Filter and analyze your portfolio companies
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

if __name__ == "__main__":
    main() 