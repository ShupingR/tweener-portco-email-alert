#!/bin/bash

# Streamlit Financial Metrics Dashboard Launcher
# Starts the interactive Streamlit dashboard for portfolio company financial metrics

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${PURPLE}💰 Streamlit Financial Metrics Dashboard${NC}"
echo -e "${BLUE}Starting interactive dashboard...${NC}"
echo ""

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo -e "${RED}Error: Could not change to script directory${NC}" >&2
    exit 1
}

# Check if virtual environment exists and activate it
if [[ -d ".venv" ]]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate || {
        echo -e "${RED}Error: Could not activate virtual environment${NC}" >&2
        exit 1
    }
else
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Consider running: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${RED}Error: .env file not found${NC}" >&2
    echo "Please create .env file with required environment variables"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if Streamlit is installed
python -c "import streamlit" 2>/dev/null || {
    echo -e "${RED}Error: Streamlit not installed${NC}" >&2
    echo "Please install Streamlit: pip install streamlit"
    exit 1
}

# Check if database exists
if [[ ! -f "tracker.db" ]]; then
    echo -e "${RED}Error: Database file 'tracker.db' not found${NC}" >&2
    echo "Please ensure the email collection system has been set up"
    exit 1
fi

# Kill any existing Flask dashboard on port 8888
if lsof -ti:8888 >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping existing Flask dashboard on port 8888...${NC}"
    pkill -f "dashboard/app.py" || true
    sleep 2
fi

# Start the Streamlit dashboard
echo -e "${GREEN}🚀 Starting Streamlit Financial Metrics Dashboard${NC}"
echo -e "${BLUE}Dashboard will open automatically in your browser${NC}"
echo -e "${BLUE}URL: http://localhost:8501${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the dashboard${NC}"
echo ""

# Run Streamlit
streamlit run dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --browser.gatherUsageStats=false 