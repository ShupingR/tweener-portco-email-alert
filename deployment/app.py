#!/usr/bin/env python3
"""
Simple Flask app to serve Streamlit dashboard on Google App Engine
"""

import os
import sys
import subprocess
import threading
import time
import requests
from flask import Flask, render_template_string, redirect, url_for

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Streamlit process
streamlit_process = None

def start_streamlit():
    """Start Streamlit in background"""
    global streamlit_process
    cmd = [
        "streamlit", "run", "dashboard/streamlit_app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    print(f"Starting Streamlit with command: {' '.join(cmd)}")
    streamlit_process = subprocess.Popen(cmd)
    return streamlit_process

def check_streamlit_health():
    """Check if Streamlit is running"""
    try:
        response = requests.get("http://localhost:8080/_stcore/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    """Main route - redirect to Streamlit"""
    if check_streamlit_health():
        return redirect("http://localhost:8080")
    else:
        return """
        <html>
        <head>
            <title>Tweener Insights Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .loading { color: #4fd1c7; }
                .error { color: #f56565; }
            </style>
        </head>
        <body>
            <h1 class="loading">🚀 Starting Tweener Insights Dashboard...</h1>
            <p>Please wait while the dashboard loads...</p>
            <script>
                setTimeout(function() {
                    window.location.reload();
                }, 5000);
            </script>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    if check_streamlit_health():
        return {"status": "healthy", "streamlit": "running"}, 200
    else:
        return {"status": "unhealthy", "streamlit": "not running"}, 503

@app.route('/_ah/start')
def app_engine_start():
    """App Engine startup hook"""
    # Start Streamlit in background
    if not streamlit_process:
        threading.Thread(target=start_streamlit, daemon=True).start()
    
    # Wait for Streamlit to start
    for i in range(30):
        if check_streamlit_health():
            print("Streamlit is running and healthy!")
            break
        time.sleep(1)
    
    return "OK", 200

if __name__ == '__main__':
    # Start Streamlit when running locally
    if os.environ.get('GAE_ENV') is None:
        start_streamlit()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 