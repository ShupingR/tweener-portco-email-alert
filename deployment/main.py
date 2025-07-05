#!/usr/bin/env python3
"""
Main entry point for Google App Engine deployment
"""

import os
import sys
import subprocess
import threading
import time
import requests

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_streamlit_health():
    """Check if Streamlit is running and healthy"""
    try:
        response = requests.get("http://localhost:8080/_stcore/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_streamlit():
    """Start Streamlit application"""
    cmd = [
        "streamlit", "run", "dashboard/streamlit_app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    
    print(f"Starting Streamlit with command: {' '.join(cmd)}")
    subprocess.run(cmd)

def main():
    """Main function to start the application"""
    print("Starting Tweener Insights Dashboard...")
    
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Wait for Streamlit to start
    print("Waiting for Streamlit to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_streamlit_health():
            print("Streamlit is running and healthy!")
            break
        time.sleep(1)
    else:
        print("Warning: Streamlit may not have started properly")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)  # Check every minute
            if not check_streamlit_health():
                print("Warning: Streamlit health check failed")
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main() 