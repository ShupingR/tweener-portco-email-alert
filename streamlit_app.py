#!/usr/bin/env python3
"""
Tweener Fund Portfolio Dashboard - Main Entry Point

This is the single entry point for the Streamlit dashboard.
All other entry points should be removed to avoid confusion.

Usage:
    streamlit run streamlit_app.py
"""

import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use an absolute path to open the dashboard file
DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), "dashboard", "pages", "tweener_insights.py")
exec(open(DASHBOARD_PATH).read()) 