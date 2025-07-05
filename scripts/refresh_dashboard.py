#!/usr/bin/env python3
"""
Dashboard Data Refresh Script

This script clears Streamlit cache and refreshes the dashboard data.
Run this when you want to see the latest data immediately.
"""

import os
import sys
import subprocess
import time

def clear_streamlit_cache():
    """Clear Streamlit cache directory"""
    cache_dir = os.path.expanduser("~/.streamlit/cache")
    if os.path.exists(cache_dir):
        print(f"🗑️  Clearing Streamlit cache: {cache_dir}")
        subprocess.run(["rm", "-rf", cache_dir], check=True)
        print("✅ Cache cleared")
    else:
        print("ℹ️  No Streamlit cache found")

def restart_dashboard():
    """Restart the Streamlit dashboard"""
    print("🔄 Restarting Streamlit dashboard...")
    
    # Kill existing Streamlit processes
    try:
        subprocess.run(["pkill", "-f", "streamlit run"], check=False)
        time.sleep(2)
    except:
        pass
    
    # Start new dashboard
    try:
        subprocess.Popen([
            "streamlit", "run", "dashboard/streamlit_app.py", 
            "--server.port", "8501"
        ])
        print("✅ Dashboard restarted at http://localhost:8501")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    print("🔄 Dashboard Data Refresh")
    print("=" * 40)
    
    # Clear cache
    clear_streamlit_cache()
    
    # Restart dashboard
    restart_dashboard()
    
    print("\n✅ Dashboard refresh complete!")
    print("📊 New data should now be visible at http://localhost:8501")

if __name__ == "__main__":
    main() 