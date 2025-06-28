#!/bin/bash
#
# Daily Email Collection Script for Tweener Fund
# ==============================================
#
# Main entry point for daily portfolio company email collection.
# This script runs the email collector with enhanced attachment detection
# and provides colored output for easy monitoring.
#
# Usage:
#     ./collect_emails.sh [OPTIONS]
#
# Options:
#     --days=N      Number of days back to check (default: 7)
#     --dry-run     Test run without saving to database
#     --stats       Show current database statistics only
#     --help        Show detailed help
#
# Examples:
#     ./collect_emails.sh                    # Daily collection (last 7 days)
#     ./collect_emails.sh --days=1           # Yesterday's emails only
#     ./collect_emails.sh --dry-run          # Test without changes
#     ./collect_emails.sh --stats            # Show current stats
#
# The script will:
# 1. Activate the Python virtual environment
# 2. Run the enhanced email collector with aggressive attachment detection
# 3. Display results with colored output and summary
# 4. Handle errors gracefully with proper exit codes
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Show help if requested
show_help() {
    echo "Daily Email Collection Script for Tweener Fund"
    echo "=============================================="
    echo ""
    echo "This script collects and processes portfolio company emails with"
    echo "enhanced attachment detection using Claude AI analysis."
    echo ""
    echo "Usage: ./collect_emails.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --days=N      Number of days back to check for emails (1-365, default: 7)"
    echo "  --dry-run     Test run - analyze emails but don't save to database"
    echo "  --stats       Show current database statistics only"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./collect_emails.sh                    # Daily collection (last 7 days)"
    echo "  ./collect_emails.sh --days=1           # Yesterday's emails only"
    echo "  ./collect_emails.sh --days=30          # Last month's emails"
    echo "  ./collect_emails.sh --dry-run          # Test without making changes"
    echo "  ./collect_emails.sh --stats            # Show database statistics"
    echo ""
    echo "Features:"
    echo "  • Enhanced attachment detection (6 different methods)"
    echo "  • Claude AI company identification"
    echo "  • Portfolio vs non-portfolio company tracking"
    echo "  • Automatic file organization by company"
    echo "  • Duplicate prevention"
    echo "  • Safe dry-run testing"
    echo ""
    echo "The system monitors emails from:"
    echo "  • scot@tweenerfund.com"
    echo "  • shuping@tweenerfund.com"
    echo "  • nikita@tweenerfund.com"
    echo "  • scot@refibuy.ai"
    echo "  • shuping.ruan@gmail.com"
    echo ""
}

# Check for help flag
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

# Main execution
print_header "🚀 Tweener Fund Email Collection System"
print_header "========================================"
print_status "Starting email collection process..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please create it with: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if required dependencies are installed
print_status "Checking dependencies..."
python -c "import anthropic, imaplib, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Required dependencies not installed!"
    print_info "Please run: pip install -r requirements.txt"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    print_error "Environment file (.env) not found!"
    print_info "Please create .env file with required credentials (see env.example)"
    exit 1
fi

# Validate arguments
for arg in "$@"; do
    if [[ "$arg" =~ ^--days=([0-9]+)$ ]]; then
        days="${BASH_REMATCH[1]}"
        if [ "$days" -lt 1 ] || [ "$days" -gt 365 ]; then
            print_error "Invalid --days value: $days (must be 1-365)"
            exit 1
        fi
    elif [[ "$arg" != "--dry-run" && "$arg" != "--stats" ]]; then
        print_error "Unknown argument: $arg"
        print_info "Use --help for usage information"
        exit 1
    fi
done

print_success "Environment validated successfully"

# Run the email collector with all passed arguments
print_status "Running enhanced email collector..."
echo ""

# Execute the Python collector
python -m pipeline.email_collector "$@"
exit_code=$?

echo ""

# Check exit status and provide appropriate feedback
if [ $exit_code -eq 0 ]; then
    print_success "Email collection completed successfully!"
    print_info "All portfolio company emails processed with enhanced attachment detection"
    
    # Show quick stats if not in stats-only mode
    stats_only=false
    for arg in "$@"; do
        if [[ "$arg" == "--stats" ]]; then
            stats_only=true
            break
        fi
    done
    
    if [ "$stats_only" = false ]; then
        print_status "Quick summary:"
        python -c "
from pipeline.email_collector import DailyEmailCollector
collector = DailyEmailCollector()
stats = collector.get_summary_stats()
print(f'   📊 Total Companies: {stats[\"total_companies\"]} ({stats[\"portfolio_companies\"]} portfolio)')
print(f'   📧 Total Emails: {stats[\"total_emails\"]}')
print(f'   📎 Total Attachments: {stats[\"total_attachments\"]}')
print(f'   🕐 Recent Activity: {stats[\"recent_emails_7d\"]} emails in last 7 days')
        "
    fi
    
else
    print_error "Email collection failed with exit code $exit_code"
    print_info "Check the error messages above for details"
    exit $exit_code
fi

print_status "Email collection process finished"
print_info "Ready for next daily run!"

# Deactivate virtual environment
deactivate 2>/dev/null || true 