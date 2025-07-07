#!/usr/bin/env python3
"""
App Engine entry point for Tweener Fund Portfolio Intelligence Platform
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Start the Streamlit application"""
    port = int(os.environ.get('PORT', 8080))
    
    # Run Streamlit
    subprocess.run([
        'streamlit', 'run', 'streamlit_app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ])

if __name__ == '__main__':
    main()
