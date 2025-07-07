#!/usr/bin/env python3
"""
Financial Metrics Dashboard - Streamlit Version

Interactive dashboard for viewing portfolio company financial metrics
with charts, filtering, and real-time data analysis.

Usage:
    streamlit run dashboard/streamlit_app.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import json
from sqlalchemy import func, text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import authentication first
try:
    from user_auth import check_authentication, show_login_page, show_user_info, require_permission
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

from database.models import Company, EmailUpdate
from database.financial_models import FinancialMetrics
from database.connection import SessionLocal

# Page configuration
st.set_page_config(
    page_title="Tweener Insights - Portfolio Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tweener Fund Brand Colors - Custom CSS
st.markdown("""
<style>
    /* Tweener Fund Brand Theme - Actual Website Colors */
    :root {
        --tweener-primary: #4fd1c7;     /* Teal/Turquoise from logo */
        --tweener-secondary: #38b2ac;   /* Darker teal */
        --tweener-accent: #81e6d9;      /* Light teal */
        --tweener-dark-green: #2d5016;  /* Dark green from footer */
        --tweener-orange: #ed8936;      /* Orange from Invest button */
        --tweener-success: #48bb78;     /* Green for positive metrics */
        --tweener-warning: #ed8936;     /* Orange for warnings */
        --tweener-danger: #f56565;      /* Red for negative metrics */
        --tweener-gray-50: #f7fafc;
        --tweener-gray-100: #edf2f7;
        --tweener-gray-200: #e2e8f0;
        --tweener-gray-300: #cbd5e0;
        --tweener-gray-600: #718096;
        --tweener-gray-700: #4a5568;
        --tweener-gray-800: #2d3748;
        --tweener-gray-900: #1a202c;
    }
    
    /* App-level styling with Tweener brand colors */
    .stApp {
        background-color: var(--tweener-gray-50) !important;
        color: var(--tweener-gray-800) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* Ensure all main content text is visible */
    .main .element-container * {
        color: var(--tweener-gray-800) !important;
    }
    
    /* Portfolio overview section specific styling */
    .main h2 {
        color: var(--tweener-gray-800) !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Force visibility for all metric text */
    .stMetric {
        background-color: white !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid var(--tweener-gray-200) !important;
    }
    
    .stMetric label {
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
    }
    
    .stMetric div[data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    /* Additional ultra-specific selectors for maximum visibility */
    .stMetric * {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    .stMetric label {
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
    }
    
    /* Nuclear option - force all metric numbers to be brownish-grey */
    [data-testid="metric-container"] * div * {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    .stMetric div[data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    .main > div {
        padding-top: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header styling */
    h1 {
        color: var(--tweener-primary) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--tweener-primary) !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Logo and header layout */
    .stImage > img {
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(79, 209, 199, 0.2) !important;
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
        object-fit: contain !important;
    }
    
    /* Header container styling */
    .main > div > div:first-child {
        background: linear-gradient(135deg, white 0%, var(--tweener-gray-50) 100%) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        margin-bottom: 2rem !important;
        border: 1px solid var(--tweener-gray-200) !important;
        box-shadow: 0 2px 4px rgba(79, 209, 199, 0.1) !important;
    }
    
    h2 {
        color: var(--tweener-gray-800) !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards with Tweener brand styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, white 0%, var(--tweener-gray-50) 100%) !important;
        border: 1px solid var(--tweener-gray-200) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 2px 4px rgba(79, 209, 199, 0.1) !important;
        border-left: 4px solid var(--tweener-primary) !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 12px rgba(79, 209, 199, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Metric label styling - ensure visibility */
    [data-testid="metric-container"] > div > div:first-child {
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metric value styling - large and visible */
    [data-testid="metric-container"] > div > div:nth-child(2) {
        color: #6B5B73 !important;
        font-weight: 400 !important;
        font-size: 2rem !important;
        line-height: 1.2 !important;
    }
    
    /* Metric delta styling if present */
    [data-testid="metric-container"] > div > div:nth-child(3) {
        color: var(--tweener-gray-600) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-top: 0.25rem !important;
    }
    
    /* Alternative selector for metric labels */
    [data-testid="metric-container"] label {
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Alternative selector for metric values */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
        font-size: 2rem !important;
    }
    
    /* Ensure all text in metrics is visible */
    [data-testid="metric-container"] div[data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="metric-container"] div[data-testid="metric-label"] {
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* Additional fallback selectors for metric values */
    .stMetric > div > div:nth-child(2) {
        color: #6B5B73 !important;
        font-weight: 400 !important;
        font-size: 2rem !important;
    }
    
    /* Target the actual value element more specifically */
    [data-testid="metric-container"] span {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    /* Override any Streamlit default styling */
    .stMetric [data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
        font-size: 2rem !important;
    }
    
    .stMetric div[data-testid="metric-value"] {
        color: #6B5B73 !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar with Tweener dark green styling */
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--tweener-dark-green) 0%, #1a4009 100%) !important;
        border-right: 3px solid var(--tweener-primary) !important;
    }
    
    div[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 {
        color: white !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stDateInput label,
    div[data-testid="stSidebar"] .stTextInput label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* Input styling in sidebar */
    div[data-testid="stSidebar"] .stSelectbox > div > div,
    div[data-testid="stSidebar"] .stDateInput > div > div,
    div[data-testid="stSidebar"] .stTextInput > div > div {
        background-color: white !important;
        color: var(--tweener-gray-800) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox > div > div:focus,
    div[data-testid="stSidebar"] .stDateInput > div > div:focus,
    div[data-testid="stSidebar"] .stTextInput > div > div:focus {
        border-color: var(--tweener-accent) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: var(--tweener-gray-100) !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        color: var(--tweener-gray-600) !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--tweener-primary) !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid var(--tweener-gray-200) !important;
        overflow: hidden !important;
    }
    
    .stDataFrame th {
        background-color: var(--tweener-primary) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    .stDataFrame td {
        border-color: var(--tweener-gray-200) !important;
    }
    
    /* Button styling with orange theme */
    .stButton > button {
        background-color: var(--tweener-orange) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #dd7324 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(237, 137, 54, 0.3) !important;
    }
    
    /* Success/Warning/Error colors for metrics */
    .metric-positive {
        color: var(--tweener-success) !important;
    }
    
    .metric-negative {
        color: var(--tweener-danger) !important;
    }
    
    .metric-neutral {
        color: var(--tweener-warning) !important;
    }
    
    /* Chart container styling */
    .stPlotlyChart {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid var(--tweener-gray-200) !important;
        padding: 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(79, 209, 199, 0.1) !important;
        border-left: 4px solid var(--tweener-primary) !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background-color: rgba(237, 137, 54, 0.1) !important;
        border-left: 4px solid var(--tweener-warning) !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background-color: rgba(245, 101, 101, 0.1) !important;
        border-left: 4px solid var(--tweener-danger) !important;
        border-radius: 8px !important;
    }
    
    /* Search input styling */
    .stTextInput > div > div {
        border-radius: 8px !important;
        border: 2px solid var(--tweener-gray-200) !important;
    }
    
    .stTextInput > div > div:focus {
        border-color: var(--tweener-primary) !important;
        box-shadow: 0 0 0 2px rgba(79, 209, 199, 0.2) !important;
    }
    
    /* Divider styling */
    hr {
        border-color: var(--tweener-gray-200) !important;
        margin: 2rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_financial_data():
    """Load financial metrics data from database"""
    session = SessionLocal()
    
    try:
        # Get all metrics with company info (only portfolio companies)
        query = session.query(FinancialMetrics).join(Company).filter(
            Company.is_tweener_portfolio == True
        ).order_by(
            FinancialMetrics.extracted_date.desc()
        ).all()
        
        # Helper function to clean values and replace N/A with dashes
        def clean_value(value):
            if value is None or value == '' or str(value).upper() == 'N/A':
                return '-'
            return str(value).strip()
        
        # Convert to DataFrame
        data = []
        for metric in query:
            data.append({
                'id': metric.id,
                'company_name': metric.company.name,
                'reporting_period': clean_value(metric.reporting_period),
                'reporting_date': metric.reporting_date,
                'extracted_date': metric.extracted_date,
                'mrr': clean_value(metric.mrr),
                'arr': clean_value(metric.arr),
                'qrr': clean_value(metric.qrr),
                'total_revenue': clean_value(metric.total_revenue),
                'cash_balance': clean_value(metric.cash_balance),
                'net_burn': clean_value(metric.net_burn),
                'gross_burn': clean_value(metric.gross_burn),
                'runway_months': clean_value(metric.runway_months),
                'customer_count': clean_value(metric.customer_count),
                'team_size': clean_value(metric.team_size),
                'arr_growth': clean_value(metric.arr_growth),
                'mrr_growth': clean_value(metric.mrr_growth),
                'revenue_growth_yoy': clean_value(metric.revenue_growth_yoy),
                'gross_margin': clean_value(metric.gross_margin),
                'key_highlights': clean_value(metric.key_highlights),
                'key_challenges': clean_value(metric.key_challenges),
                'funding_status': clean_value(metric.funding_status),
                'source_type': clean_value(metric.source_type),
                'source_file': clean_value(metric.source_file),
                'extraction_confidence': clean_value(metric.extraction_confidence)
            })
        
        df = pd.DataFrame(data)
        
        # Get summary statistics
        total_metrics = len(df)
        companies_with_metrics = df['company_name'].nunique() if len(df) > 0 else 0
        
        # Get total companies
        total_companies = session.query(Company).filter(Company.is_tweener_portfolio == True).count()
        
        # Recent metrics (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_metrics = len(df[df['extracted_date'] >= recent_cutoff]) if len(df) > 0 else 0
        
        stats = {
            'total_metrics': total_metrics,
            'companies_with_metrics': companies_with_metrics,
            'total_companies': total_companies,
            'recent_metrics': recent_metrics,
            'coverage_percent': round((companies_with_metrics/total_companies)*100, 1) if total_companies > 0 else 0
        }
        
        return df, stats
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), {
            'total_metrics': 0,
            'companies_with_metrics': 0,
            'total_companies': 0,
            'recent_metrics': 0,
            'coverage_percent': 0
        }
    finally:
        session.close()

def parse_financial_value(value):
    """Parse financial values like '$1.2M', '~$8.000M' to numeric"""
    if pd.isna(value) or value == '-' or not value:
        return None
    
    # Remove common prefixes and suffixes
    clean_value = str(value).replace('$', '').replace(',', '').replace('~', '').strip()
    
    # Handle M (millions) and K (thousands)
    multiplier = 1
    if clean_value.endswith('M'):
        multiplier = 1000000
        clean_value = clean_value[:-1]
    elif clean_value.endswith('K'):
        multiplier = 1000
        clean_value = clean_value[:-1]
    
    # Try to convert to float
    try:
        return float(clean_value) * multiplier
    except:
        return None

def create_arr_chart(df):
    """Create ARR comparison chart with Tweener Fund brand colors"""
    if df.empty:
        return None
    
    # Parse ARR values
    df_arr = df.copy()
    df_arr['arr_numeric'] = df_arr['arr'].apply(parse_financial_value)
    df_arr = df_arr.dropna(subset=['arr_numeric'])
    df_arr = df_arr[df_arr['arr_numeric'] > 0]
    
    if df_arr.empty:
        return None
    
    # Get latest ARR for each company (by reporting date when available)
    date_col = 'reporting_date' if 'reporting_date' in df_arr.columns and df_arr['reporting_date'].notna().any() else 'extracted_date'
    latest_arr = df_arr.loc[df_arr.groupby('company_name')[date_col].idxmax()]
    latest_arr = latest_arr.sort_values('arr_numeric', ascending=True)
    
    # Tweener Fund brand color scale - Teal theme
    tweener_color_scale = [
        [0.0, '#f7fafc'],    # Very light gray
        [0.2, '#c6f7e9'],    # Light teal
        [0.4, '#9decdb'],    # Medium light teal
        [0.6, '#81e6d9'],    # Medium teal
        [0.8, '#4fd1c7'],    # Tweener accent teal
        [1.0, '#38b2ac']     # Tweener primary teal
    ]
    
    fig = px.bar(
        latest_arr,
        x='arr_numeric',
        y='company_name',
        title='Annual Recurring Revenue (ARR) by Company',
        labels={'arr_numeric': 'ARR ($)', 'company_name': 'Company'},
        orientation='h',
        color='arr_numeric',
        color_continuous_scale=tweener_color_scale
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_tickformat='$,.0f',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color='#1a202c'),
        title_font=dict(size=18, color='#4fd1c7', family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        ),
        yaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        )
    )
    
    return fig

def create_growth_chart(df):
    """Create growth rate chart with Tweener Fund brand colors"""
    if df.empty:
        return None
    
    # Parse growth values
    df_growth = df.copy()
    df_growth['arr_growth_numeric'] = df_growth['arr_growth'].apply(
        lambda x: float(str(x).replace('%', '').replace('+', '')) if pd.notna(x) and x != '-' and '%' in str(x) else None
    )
    
    df_growth = df_growth.dropna(subset=['arr_growth_numeric'])
    
    if df_growth.empty:
        return None
    
    # Get latest growth for each company
    latest_growth = df_growth.loc[df_growth.groupby('company_name')['extracted_date'].idxmax()]
    latest_growth = latest_growth.sort_values('arr_growth_numeric', ascending=False)
    
    # Tweener Fund brand colors for positive/negative growth
    colors = ['#48bb78' if x > 0 else '#f56565' for x in latest_growth['arr_growth_numeric']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=latest_growth['company_name'],
            y=latest_growth['arr_growth_numeric'],
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in latest_growth['arr_growth_numeric']],
            textposition='outside',
            marker=dict(
                line=dict(color='#e5e7eb', width=1)
            )
        )
    ])
    
    fig.update_layout(
        title='ARR Growth Rate by Company',
        xaxis_title='Company',
        yaxis_title='Growth Rate (%)',
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color='#1a202c'),
        title_font=dict(size=18, color='#4fd1c7', family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        ),
        yaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        )
    )
    
    return fig

def create_cash_runway_chart(df):
    """Create cash and runway chart"""
    if df.empty:
        return None
    
    # Parse cash and runway values
    df_cash = df.copy()
    df_cash['cash_numeric'] = df_cash['cash_balance'].apply(parse_financial_value)
    
    # Create a robust runway parsing function
    def safe_parse_runway(value):
        """Safely parse runway values like '12 months', '12-18', '6+' to numeric"""
        if pd.isna(value) or value == '-' or not value:
            return None
        
        try:
            # Convert to string and clean basic formatting
            clean_value = str(value).lower()
            clean_value = clean_value.replace('months', '').replace('month', '').replace('+', '').strip()
            
            # Handle empty after cleaning
            if not clean_value:
                return None
            
            # Handle ranges like "12-18" - take the midpoint
            if '-' in clean_value:
                try:
                    parts = [p.strip() for p in clean_value.split('-')]
                    if len(parts) == 2 and parts[0] and parts[1]:
                        num1 = float(parts[0])
                        num2 = float(parts[1])
                        return (num1 + num2) / 2
                except (ValueError, IndexError):
                    pass
            
            # Handle single numeric values
            try:
                return float(clean_value)
            except ValueError:
                return None
                
        except Exception:
            return None
    
    # Apply the safe parsing function
    df_cash['runway_numeric'] = df_cash['runway_months'].apply(safe_parse_runway)
    
    # Remove rows where we couldn't parse both cash and runway
    df_cash = df_cash.dropna(subset=['cash_numeric', 'runway_numeric'])
    
    if df_cash.empty:
        return None
    
    # Get latest data for each company (by reporting date when available)
    date_col = 'reporting_date' if 'reporting_date' in df_cash.columns and df_cash['reporting_date'].notna().any() else 'extracted_date'
    latest_cash = df_cash.loc[df_cash.groupby('company_name')[date_col].idxmax()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=latest_cash['cash_numeric'],
        y=latest_cash['runway_numeric'],
        mode='markers+text',
        text=latest_cash['company_name'],
        textposition='top center',
        marker=dict(
            size=12, 
            color='#4fd1c7', 
            opacity=0.8,
            line=dict(color='#38b2ac', width=2)
        ),
        name='Companies'
    ))
    
    fig.update_layout(
        title='Cash Balance vs Runway',
        xaxis_title='Cash Balance ($)',
        yaxis_title='Runway (Months)',
        height=400,
        xaxis_tickformat='$,.0f',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color='#1a202c'),
        title_font=dict(size=18, color='#4fd1c7', family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        ),
        yaxis=dict(
            gridcolor='#edf2f7', 
            showgrid=True,
            tickfont=dict(color='#1a202c', size=12),
            title=dict(font=dict(color='#1a202c', size=14, family="Inter, sans-serif"))
        )
    )
    
    return fig

# Chatbot Functionality
class DatabaseChatbot:
    def __init__(self):
        self.session = SessionLocal()
        self.conversation_history = []
    
    def close_session(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    def query_database(self, question):
        """Process natural language questions about the portfolio data"""
        question_lower = question.lower()
        
        try:
            # Company-specific queries
            if "company" in question_lower or "companies" in question_lower:
                return self._handle_company_queries(question_lower)
            
            # Financial metrics queries
            elif any(term in question_lower for term in ["arr", "revenue", "mrr", "financial"]):
                return self._handle_financial_queries(question_lower)
            
            # Growth queries
            elif "growth" in question_lower:
                return self._handle_growth_queries(question_lower)
            
            # Cash and runway queries
            elif any(term in question_lower for term in ["cash", "runway", "burn"]):
                return self._handle_cash_queries(question_lower)
            
            # Team and customer queries
            elif any(term in question_lower for term in ["team", "employees", "customers", "hiring"]):
                return self._handle_operational_queries(question_lower)
            
            # General portfolio overview
            elif any(term in question_lower for term in ["overview", "summary", "portfolio", "total"]):
                return self._handle_portfolio_overview()
            
            # Recent updates
            elif any(term in question_lower for term in ["recent", "latest", "new", "updates"]):
                return self._handle_recent_updates()
            
            # Performance queries
            elif any(term in question_lower for term in ["performance", "best", "worst", "top", "bottom"]):
                return self._handle_performance_queries(question_lower)
            
            else:
                return self._provide_help()
                
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}. Please try rephrasing your question."
    
    def _handle_company_queries(self, question):
        """Handle company-related queries"""
        try:
            companies = self.session.query(Company).filter(Company.is_tweener_portfolio == True).all()
            
            if "how many" in question or "count" in question:
                total_companies = len(companies)
                companies_with_metrics = self.session.query(FinancialMetrics.company_id).distinct().count()
                return f"We track {total_companies} portfolio companies in total, with {companies_with_metrics} companies having financial metrics data."
            
            elif "list" in question or "all companies" in question:
                company_names = [c.name for c in companies]
                if len(company_names) > 10:
                    return f"Here are our portfolio companies: {', '.join(company_names[:10])}... and {len(company_names)-10} more. Total: {len(company_names)} companies."
                else:
                    return f"Our portfolio companies: {', '.join(company_names)}"
            
            else:
                # Check if asking about a specific company
                for company in companies:
                    if company.name.lower() in question:
                        return self._get_company_details(company.name)
                
                return "I can help you with company information. Try asking 'How many companies?' or 'List all companies' or ask about a specific company by name."
        
        except Exception as e:
            return f"Error retrieving company data: {str(e)}"
    
    def _handle_financial_queries(self, question):
        """Handle financial metrics queries"""
        try:
            # Get latest financial metrics (only portfolio companies)
            latest_metrics = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(10).all()
            
            if not latest_metrics:
                return "No financial metrics data available yet."
            
            if "arr" in question:
                arr_data = [m for m in latest_metrics if m.arr and m.arr != 'N/A' and m.arr != '-']
                if arr_data:
                    total_arr = sum(self._parse_financial_value(m.arr) for m in arr_data if self._parse_financial_value(m.arr) > 0)
                    return f"Based on latest data, our portfolio companies have a combined ARR of approximately ${total_arr:,.0f}. Data from {len(arr_data)} companies."
                else:
                    return "No ARR data available in recent metrics."
            
            elif "mrr" in question:
                mrr_data = [m for m in latest_metrics if m.mrr and m.mrr != 'N/A' and m.mrr != '-']
                if mrr_data:
                    total_mrr = sum(self._parse_financial_value(m.mrr) for m in mrr_data if self._parse_financial_value(m.mrr) > 0)
                    return f"Based on latest data, our portfolio companies have a combined MRR of approximately ${total_mrr:,.0f}. Data from {len(mrr_data)} companies."
                else:
                    return "No MRR data available in recent metrics."
            
            else:
                return "I can help with ARR, MRR, and other financial metrics. Try asking 'What's our total ARR?' or 'Show me MRR data'."
        
        except Exception as e:
            return f"Error retrieving financial data: {str(e)}"
    
    def _handle_growth_queries(self, question):
        """Handle growth-related queries"""
        try:
            growth_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.arr_growth.isnot(None),
                FinancialMetrics.arr_growth != 'N/A',
                FinancialMetrics.arr_growth != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
            
            if not growth_data:
                return "No growth data available in recent metrics."
            
            # Parse growth rates
            growth_rates = []
            for metric in growth_data:
                try:
                    # Extract percentage from strings like "+25%" or "148.509%"
                    growth_str = str(metric.arr_growth).replace('+', '').replace('%', '')
                    growth_rate = float(growth_str)
                    growth_rates.append((metric.company.name, growth_rate))
                except:
                    continue
            
            if growth_rates:
                avg_growth = sum(rate for _, rate in growth_rates) / len(growth_rates)
                best_growth = max(growth_rates, key=lambda x: x[1])
                
                return f"Portfolio growth insights:\n• Average growth rate: {avg_growth:.1f}%\n• Best performing: {best_growth[0]} at {best_growth[1]:.1f}%\n• Data from {len(growth_rates)} companies"
            else:
                return "Unable to parse growth data from recent metrics."
        
        except Exception as e:
            return f"Error retrieving growth data: {str(e)}"
    
    def _handle_cash_queries(self, question):
        """Handle cash and runway queries"""
        try:
            cash_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.cash_balance.isnot(None),
                FinancialMetrics.cash_balance != 'N/A',
                FinancialMetrics.cash_balance != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
            
            if "runway" in question:
                runway_data = [m for m in cash_data if m.runway_months and m.runway_months not in ['N/A', '-']]
                if runway_data:
                    avg_runway = sum(self._parse_runway_months(m.runway_months) for m in runway_data) / len(runway_data)
                    return f"Portfolio runway insights:\n• Average runway: {avg_runway:.1f} months\n• Data from {len(runway_data)} companies\n• Companies should maintain 12+ months runway"
                else:
                    return "No runway data available in recent metrics."
            
            elif "cash" in question:
                if cash_data:
                    total_cash = sum(self._parse_financial_value(m.cash_balance) for m in cash_data if self._parse_financial_value(m.cash_balance) > 0)
                    return f"Portfolio cash insights:\n• Combined cash balance: ${total_cash:,.0f}\n• Data from {len(cash_data)} companies"
                else:
                    return "No cash balance data available in recent metrics."
        
        except Exception as e:
            return f"Error retrieving cash/runway data: {str(e)}"
    
    def _handle_operational_queries(self, question):
        """Handle team size and customer queries"""
        try:
            if "team" in question or "employees" in question:
                team_data = self.session.query(FinancialMetrics).join(Company).filter(
                    Company.is_tweener_portfolio == True,
                    FinancialMetrics.team_size.isnot(None),
                    FinancialMetrics.team_size != 'N/A',
                    FinancialMetrics.team_size != '-'
                ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
                
                if team_data:
                    total_employees = sum(int(float(str(m.team_size))) for m in team_data if str(m.team_size).replace('.', '').isdigit())
                    return f"Portfolio team insights:\n• Total employees across portfolio: {total_employees}\n• Data from {len(team_data)} companies"
                else:
                    return "No team size data available in recent metrics."
            
            elif "customer" in question:
                customer_data = self.session.query(FinancialMetrics).join(Company).filter(
                    Company.is_tweener_portfolio == True,
                    FinancialMetrics.customer_count.isnot(None),
                    FinancialMetrics.customer_count != 'N/A',
                    FinancialMetrics.customer_count != '-'
                ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
                
                if customer_data:
                    total_customers = sum(int(float(str(m.customer_count))) for m in customer_data if str(m.customer_count).replace('.', '').isdigit())
                    return f"Portfolio customer insights:\n• Total customers across portfolio: {total_customers:,}\n• Data from {len(customer_data)} companies"
                else:
                    return "No customer count data available in recent metrics."
        
        except Exception as e:
            return f"Error retrieving operational data: {str(e)}"
    
    def _handle_portfolio_overview(self):
        """Provide portfolio overview"""
        try:
            total_companies = self.session.query(Company).filter(Company.is_tweener_portfolio == True).count()
            companies_with_metrics = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).distinct(FinancialMetrics.company_id).count()
            recent_updates = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.extracted_date >= datetime.now() - timedelta(days=30)
            ).count()
            
            overview = f"""📊 **Portfolio Overview:**
• **Total Companies:** {total_companies}
• **Companies with Metrics:** {companies_with_metrics}
• **Coverage:** {(companies_with_metrics/total_companies*100):.1f}%
• **Recent Updates (30 days):** {recent_updates}

The dashboard shows detailed financial metrics, growth rates, and operational data for our portfolio companies."""
            
            return overview
        
        except Exception as e:
            return f"Error generating portfolio overview: {str(e)}"
    
    def _handle_recent_updates(self):
        """Show recent updates"""
        try:
            recent = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).order_by(
                FinancialMetrics.extracted_date.desc()
            ).limit(5).all()
            
            if not recent:
                return "No recent updates available."
            
            updates = "📅 **Recent Updates:**\n"
            for metric in recent:
                updates += f"• **{metric.company.name}** - {metric.extracted_date.strftime('%Y-%m-%d')}"
                if metric.arr and metric.arr not in ['N/A', '-']:
                    updates += f" (ARR: {metric.arr})"
                updates += "\n"
            
            return updates
        
        except Exception as e:
            return f"Error retrieving recent updates: {str(e)}"
    
    def _handle_performance_queries(self, question):
        """Handle performance comparison queries"""
        try:
            if "best" in question or "top" in question:
                # Find companies with highest growth (only portfolio companies)
                growth_data = self.session.query(FinancialMetrics).join(Company).filter(
                    Company.is_tweener_portfolio == True,
                    FinancialMetrics.arr_growth.isnot(None),
                    FinancialMetrics.arr_growth != 'N/A',
                    FinancialMetrics.arr_growth != '-'
                ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
                
                if growth_data:
                    company_growth = {}
                    for metric in growth_data:
                        try:
                            growth_str = str(metric.arr_growth).replace('+', '').replace('%', '')
                            growth_rate = float(growth_str)
                            if metric.company.name not in company_growth or growth_rate > company_growth[metric.company.name]:
                                company_growth[metric.company.name] = growth_rate
                        except:
                            continue
                    
                    if company_growth:
                        top_performers = sorted(company_growth.items(), key=lambda x: x[1], reverse=True)[:3]
                        result = "🚀 **Top Performing Companies (by Growth):**\n"
                        for i, (company, growth) in enumerate(top_performers, 1):
                            result += f"{i}. **{company}**: {growth:.1f}% growth\n"
                        return result
            
            return "I can help identify top performers. Try asking 'Which companies are performing best?' or 'Show me top growth companies'."
        
        except Exception as e:
            return f"Error analyzing performance: {str(e)}"
    
    def _get_company_details(self, company_name):
        """Get detailed information about a specific company"""
        try:
            company = self.session.query(Company).filter(
                Company.is_tweener_portfolio == True,
                Company.name.ilike(f"%{company_name}%")
            ).first()
            if not company:
                return f"Company '{company_name}' not found in our portfolio."
            
            # Get latest metrics for this company
            latest_metric = self.session.query(FinancialMetrics).filter(
                FinancialMetrics.company_id == company.id
            ).order_by(FinancialMetrics.extracted_date.desc()).first()
            
            if not latest_metric:
                return f"**{company.name}** is in our portfolio, but no financial metrics are available yet."
            
            details = f"""📈 **{company.name} - Latest Metrics:**
• **Last Updated:** {latest_metric.extracted_date.strftime('%Y-%m-%d')}
• **ARR:** {latest_metric.arr if latest_metric.arr not in ['N/A', '-'] else 'Not available'}
• **MRR:** {latest_metric.mrr if latest_metric.mrr not in ['N/A', '-'] else 'Not available'}
• **Growth:** {latest_metric.arr_growth if latest_metric.arr_growth not in ['N/A', '-'] else 'Not available'}
• **Cash Balance:** {latest_metric.cash_balance if latest_metric.cash_balance not in ['N/A', '-'] else 'Not available'}
• **Runway:** {latest_metric.runway_months if latest_metric.runway_months not in ['N/A', '-'] else 'Not available'}
• **Team Size:** {latest_metric.team_size if latest_metric.team_size not in ['N/A', '-'] else 'Not available'}
• **Customers:** {latest_metric.customer_count if latest_metric.customer_count not in ['N/A', '-'] else 'Not available'}"""
            
            return details
        
        except Exception as e:
            return f"Error retrieving company details: {str(e)}"
    
    def _provide_help(self):
        """Provide help information"""
        return """🤖 **I can help you with:**

**Company Information:**
• "How many companies do we track?"
• "List all companies"
• "Tell me about [Company Name]"

**Financial Metrics:**
• "What's our total ARR?"
• "Show me MRR data"
• "Financial overview"

**Growth Analysis:**
• "Which companies are growing fastest?"
• "Show me growth rates"

**Cash & Runway:**
• "How much cash do we have?"
• "What's our average runway?"

**Operations:**
• "How many employees across portfolio?"
• "Customer count summary"

**General:**
• "Portfolio overview"
• "Recent updates"
• "Top performers"

Just ask me a question about our portfolio companies!"""
    
    def _parse_financial_value(self, value_str):
        """Parse financial values using centralized formatter"""
        from utils.financial_formatter import FinancialMetricsFormatter
        formatter = FinancialMetricsFormatter()
        parsed = formatter.parse_currency(value_str)
        return parsed if parsed is not None else 0
    
    def _parse_runway_months(self, runway_str):
        """Parse runway months using centralized formatter"""
        from utils.financial_formatter import FinancialMetricsFormatter
        formatter = FinancialMetricsFormatter()
        parsed = formatter.parse_runway(runway_str)
        return parsed if parsed is not None else 0

def create_chatbot_ui():
    """Create the chatbot UI component - disabled for now"""
    # Chatbot functionality temporarily disabled
    pass

def main():
    # Check authentication first
    if not AUTH_AVAILABLE:
        st.error("Authentication system not available. Please install required dependencies.")
        st.info("For local development, install: pip install google-cloud-secret-manager")
        return
    
    # Check authentication
    if not check_authentication():
        show_login_page()
        return
    
    # Show user info in sidebar
    show_user_info()
    
    # Check read permission
    require_permission("read", "You need read access to view the Tweener Insights dashboard.")
    
    # Simple header
    st.title("Tweener Insights")
    st.markdown("**Generative Portfolio Intelligence for Triangle Tweener Fund**")
    
    st.markdown("---")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Data", key="refresh_data"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.markdown("*Click to refresh data from database*")
    
    # Load data
    with st.spinner("Loading financial data..."):
        df, stats = load_financial_data()
    
    # Overview Statistics
    st.header("📊 Portfolio Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Companies Tracked",
            value=f"{stats['companies_with_metrics']}/{stats['total_companies']}",
            help="Portfolio companies with financial metrics"
        )
    
    with col2:
        st.metric(
            label="Portfolio Coverage",
            value=f"{stats['coverage_percent']}%",
            help="Percentage of portfolio companies with metrics"
        )
    
    with col3:
        st.metric(
            label="Recent Updates",
            value=stats['recent_metrics'],
            help="Metrics extracted in the last 30 days"
        )
    
    if df.empty:
        st.warning("No financial metrics data available. Run the financial metrics processor to extract data from emails.")
        return
    
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Company filter
    companies = ['All'] + sorted(df['company_name'].unique().tolist())
    selected_company = st.sidebar.selectbox("Select Company", companies)
    
    # Data Quality Confidence filter
    confidence_levels = ['All'] + sorted(df['extraction_confidence'].dropna().unique().tolist())
    selected_confidence = st.sidebar.selectbox("Data Quality Confidence", confidence_levels)
    
    # Source filter
    sources = ['All'] + sorted(df['source_type'].dropna().unique().tolist())
    selected_source = st.sidebar.selectbox("Data Source", sources)
    
    # Date range filter (use reporting date if available, otherwise extracted date)
    if not df.empty:
        # Use reporting_date for filtering when available, fall back to extracted_date
        date_col = 'reporting_date' if 'reporting_date' in df.columns and df['reporting_date'].notna().any() else 'extracted_date'
        valid_dates = df[df[date_col].notna()][date_col]
        
        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            date_range = st.sidebar.date_input(
                "Reporting Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter by the period the metrics represent (not when they were extracted)"
            )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['company_name'] == selected_company]
    
    if selected_confidence != 'All':
        filtered_df = filtered_df[filtered_df['extraction_confidence'] == selected_confidence]
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['source_type'] == selected_source]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        # Use the same date column for filtering as we used for the date picker
        date_col = 'reporting_date' if 'reporting_date' in filtered_df.columns and filtered_df['reporting_date'].notna().any() else 'extracted_date'
        filtered_df = filtered_df[
            (filtered_df[date_col].dt.date >= start_date) &
            (filtered_df[date_col].dt.date <= end_date)
        ]
    
    # Charts Section
    st.header("📈 Financial Analysis")
    
    tab1, tab2, tab3 = st.tabs(["💰 Revenue Metrics", "📊 Growth Analysis", "💵 Cash & Runway"])
    
    with tab1:
        arr_chart = create_arr_chart(filtered_df)
        if arr_chart:
            st.plotly_chart(arr_chart, use_container_width=True)
        else:
            st.info("No ARR data available for the selected filters.")
    
    with tab2:
        growth_chart = create_growth_chart(filtered_df)
        if growth_chart:
            st.plotly_chart(growth_chart, use_container_width=True)
        else:
            st.info("No growth data available for the selected filters.")
    
    with tab3:
        cash_chart = create_cash_runway_chart(filtered_df)
        if cash_chart:
            st.plotly_chart(cash_chart, use_container_width=True)
        else:
            st.info("No cash/runway data available for the selected filters.")
    
    st.markdown("---")
    
    # Company Summary
    if not filtered_df.empty:
        st.header("🏢 Company Summary")
        
        # Group by company and get latest metrics (by reporting date when available)
        company_summary = []
        for company in filtered_df['company_name'].unique():
            company_data = filtered_df[filtered_df['company_name'] == company]
            # Use reporting_date for finding latest, fall back to extracted_date
            date_col = 'reporting_date' if 'reporting_date' in company_data.columns and company_data['reporting_date'].notna().any() else 'extracted_date'
            latest = company_data.loc[company_data[date_col].idxmax()]
            
            company_summary.append({
                'Company': company,
                'Latest Update': latest[date_col].strftime('%Y-%m-%d'),
                'ARR': latest['arr'] if latest['arr'] != '-' else '-',
                'MRR': latest['mrr'] if latest['mrr'] != '-' else '-',
                'Cash Balance': latest['cash_balance'] if latest['cash_balance'] != '-' else '-',
                'Runway': latest['runway_months'] if latest['runway_months'] != '-' else '-',
                'Growth': latest['arr_growth'] if latest['arr_growth'] != '-' else '-',
                'Customers': latest['customer_count'] if latest['customer_count'] != '-' else '-',
                'Team Size': latest['team_size'] if latest['team_size'] != '-' else '-',
                'Data Quality': latest['extraction_confidence'],
                'Records': len(company_data)
            })
        
        summary_df = pd.DataFrame(company_summary)
        st.dataframe(summary_df, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Data Table
    st.header("📋 Detailed Financial Metrics")
    
    # Search functionality
    search_term = st.text_input("🔍 Search metrics", placeholder="Search companies, metrics, or periods...")
    
    if search_term:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    
    if not display_df.empty:
        # Select columns to display
        display_columns = [
            'company_name', 'reporting_period', 'arr', 'mrr', 'cash_balance', 
            'runway_months', 'arr_growth', 'customer_count', 'team_size',
            'source_type', 'extraction_confidence', 'extracted_date'
        ]
        
        # Format the dataframe for display
        display_data = display_df[display_columns].copy()
        display_data['extracted_date'] = display_data['extracted_date'].dt.strftime('%Y-%m-%d')
        
        # Rename columns for better display
        display_data.columns = [
            'Company', 'Period', 'ARR', 'MRR', 'Cash Balance', 
            'Runway', 'Growth', 'Customers', 'Team Size',
            'Source', 'Data Quality', 'Extracted'
        ]
        
        st.dataframe(display_data, use_container_width=True)
        
        # Download button
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"financial_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data matches the current filters.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**Data source:** Portfolio company email updates and attachments")

if __name__ == "__main__":
    main() 