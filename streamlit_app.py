#!/usr/bin/env python3
"""
Streamlit App Entry Point for Tweener Fund Portfolio Dashboard

This file serves as the main entry point for the Streamlit dashboard.
It imports and runs the main dashboard functionality.
"""

import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Run the dashboard code directly (not as an import)
exec(open('dashboard/Tweener_Insights.py').read()) 