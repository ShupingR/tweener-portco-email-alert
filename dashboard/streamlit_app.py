#!/usr/bin/env python3
"""
Streamlit App Entry Point for Tweener Fund Portfolio Dashboard

This file serves as the main entry point for the Streamlit dashboard.
It imports and runs the main dashboard functionality.
"""

import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main dashboard functionality
from dashboard.Tweener_Insights import main

def app():
    """Main app function"""
    # Run the main dashboard
    main()

if __name__ == "__main__":
    app() 