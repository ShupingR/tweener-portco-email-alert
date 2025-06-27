#!/bin/bash
#
# Email Collection Wrapper Script
# ===============================
#
# Main entry point for the Tweener Fund email collection system.
# This script runs the daily email collector with proper error handling
# and colored output for easy monitoring.
#
# Usage:
#     ./collect_emails.sh [--days=N] [--dry-run] [--stats]
#
# The script will:
# 1. Activate the Python virtual environment
# 2. Run the email collector from the pipeline module
# 3. Display results with colored output
# 4. Handle errors gracefully
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main execution
print_status "Starting Tweener Fund Email Collection"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if required dependencies are installed
python -c "import anthropic, imaplib, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Required dependencies not installed. Please run: pip install -r requirements.txt"
    exit 1
fi

# Run the email collector with all passed arguments
print_status "Running email collector..."
python -m pipeline.email_collector "$@"

# Check exit status
if [ $? -eq 0 ]; then
    print_success "Email collection completed successfully"
else
    print_error "Email collection failed"
    exit 1
fi

print_status "Email collection finished" 