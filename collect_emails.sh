#!/bin/bash
# Daily Email Collection Script for Tweener Fund
# ==============================================
# 
# Simple wrapper script for daily email collection.
# Can be run manually or scheduled via cron.
#
# Usage:
#   ./collect_emails.sh           # Normal run (7 days)
#   ./collect_emails.sh --dry-run # Test run
#   ./collect_emails.sh --stats   # Show statistics only

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found! Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found! Please copy env.example to .env and configure your credentials."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if required Python packages are installed
print_status "Checking dependencies..."
python -c "import anthropic, imaplib, sqlalchemy" 2>/dev/null || {
    print_error "Required Python packages not installed! Please run: pip install -r requirements.txt"
    exit 1
}

# Run the email collector
print_status "Starting email collection..."
echo

# Pass all arguments to the Python script
if python daily_email_collector.py "$@"; then
    print_success "Email collection completed successfully!"
else
    print_error "Email collection failed!"
    exit 1
fi

echo
print_status "Email collection script finished." 