#!/bin/bash

# Financial Metrics Processor Shell Wrapper
# Easy-to-use script for extracting financial metrics from portfolio company updates

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
DAYS=30
DRY_RUN=false
STATS=false
EXPORT=""
EMAIL_ID=""
COMPANY=""

# Function to show usage
show_usage() {
    echo -e "${BLUE}Financial Metrics Processor${NC}"
    echo "Extract financial metrics from portfolio company email updates"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --days N         Process emails from last N days (default: 30)"
    echo "  -e, --email-id ID    Process specific email update by ID"
    echo "  -c, --company NAME   Process emails for specific company"
    echo "  -n, --dry-run        Show what would be processed without making changes"
    echo "  -s, --stats          Show current financial metrics statistics"
    echo "  -x, --export [FILE]  Export financial metrics to CSV file"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --stats                    # Show current statistics"
    echo "  $0 --days 7                   # Process last 7 days"
    echo "  $0 --company Validic          # Process all Validic emails"
    echo "  $0 --email-id 123             # Process specific email"
    echo "  $0 --dry-run --days 14        # See what would be processed"
    echo "  $0 --export metrics.csv       # Export to CSV file"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--days)
            DAYS="$2"
            shift 2
            ;;
        -e|--email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        -c|--company)
            COMPANY="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -s|--stats)
            STATS=true
            shift
            ;;
        -x|--export)
            if [[ -n $2 && $2 != -* ]]; then
                EXPORT="$2"
                shift 2
            else
                EXPORT="financial_metrics_export.csv"
                shift
            fi
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo -e "${RED}Error: Could not change to script directory${NC}" >&2
    exit 1
}

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Consider running: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
fi

# Activate virtual environment if it exists
if [[ -d ".venv" ]]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate || {
        echo -e "${RED}Error: Could not activate virtual environment${NC}" >&2
        exit 1
    }
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${RED}Error: .env file not found${NC}" >&2
    echo "Please create .env file with required environment variables"
    echo "See env.example for template"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Verify required environment variables
if [[ -z "$ANTHROPIC_API_KEY" ]]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set in .env file${NC}" >&2
    exit 1
fi

# Build Python command
PYTHON_CMD="python process_financial_metrics.py"

if [[ "$STATS" == "true" ]]; then
    PYTHON_CMD="$PYTHON_CMD --stats"
elif [[ -n "$EXPORT" ]]; then
    PYTHON_CMD="$PYTHON_CMD --export $EXPORT"
elif [[ -n "$EMAIL_ID" ]]; then
    PYTHON_CMD="$PYTHON_CMD --email-id $EMAIL_ID"
    if [[ "$DRY_RUN" == "true" ]]; then
        PYTHON_CMD="$PYTHON_CMD --dry-run"
    fi
elif [[ -n "$COMPANY" ]]; then
    PYTHON_CMD="$PYTHON_CMD --company \"$COMPANY\""
    if [[ "$DRY_RUN" == "true" ]]; then
        PYTHON_CMD="$PYTHON_CMD --dry-run"
    fi
else
    PYTHON_CMD="$PYTHON_CMD --days $DAYS"
    if [[ "$DRY_RUN" == "true" ]]; then
        PYTHON_CMD="$PYTHON_CMD --dry-run"
    fi
fi

# Show what we're about to run
echo -e "${PURPLE}Financial Metrics Processor${NC}"
echo -e "${BLUE}Running: $PYTHON_CMD${NC}"
echo ""

# Record start time
START_TIME=$(date +%s)

# Run the Python script
eval $PYTHON_CMD
EXIT_CODE=$?

# Record end time and calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Processing completed successfully in ${DURATION}s${NC}"
else
    echo -e "${RED}❌ Processing failed with exit code $EXIT_CODE${NC}"
fi

exit $EXIT_CODE 