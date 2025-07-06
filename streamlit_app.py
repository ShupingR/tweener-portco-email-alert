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

# Import and run the main dashboard
from dashboard.tweener_insights import main

# Run the main function
if __name__ == "__main__":
    main() 