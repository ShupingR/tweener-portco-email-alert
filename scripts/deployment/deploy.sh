#!/bin/bash
"""
Tweener Fund Dashboard - Unified Deployment Script

This script consolidates all deployment options into a single, clear interface.
Replaces multiple confusing deployment scripts.

Usage:
    ./scripts/deployment/deploy.sh [options]

Options:
    --local          Deploy locally with Docker
    --streamlit-cloud Deploy to Streamlit Community Cloud
    --test           Test deployment locally
    --help           Show this help message

Examples:
    ./scripts/deployment/deploy.sh --local
    ./scripts/deployment/deploy.sh --streamlit-cloud
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="tweener-dashboard"

# Functions
print_header() {
    echo -e "${BLUE}🚀 $1${NC}"
    echo "=================================="
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

check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check for required tools
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    print_success "Dependencies check complete"
}

deploy_local() {
    print_header "Deploying Locally with Docker"
    
    # Build Docker image
    print_header "Building Docker Image"
    docker build -t $PROJECT_NAME .
    
    # Run container
    print_header "Starting Container"
    docker run -d \
        --name $PROJECT_NAME \
        -p 8501:8501 \
        -e STREAMLIT_SERVER_PORT=8501 \
        $PROJECT_NAME
    
    print_success "Dashboard deployed locally!"
    echo "Access at: http://localhost:8501"
    echo "Stop with: docker stop $PROJECT_NAME"
}

deploy_streamlit_cloud() {
    print_header "Deploying to Streamlit Community Cloud"
    
    print_warning "This will guide you through Streamlit Cloud deployment"
    echo ""
    echo "Steps:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Configure:"
    echo "   - Repository: ShupingR/tweener-portco-email-alert"
    echo "   - Branch: main"
    echo "   - Main file path: streamlit_app.py"
    echo "5. Add secrets in Settings → Secrets"
    echo "6. Deploy!"
    echo ""
    echo "For detailed instructions, see STREAMLIT_CLOUD_DEPLOYMENT.md"
    
    print_success "Streamlit Cloud deployment guide displayed"
}

test_deployment() {
    print_header "Testing Deployment Locally"
    
    # Build image
    docker build -t $PROJECT_NAME-test .
    
    # Run test container
    docker run --rm -p 8501:8501 $PROJECT_NAME-test &
    TEST_PID=$!
    
    # Wait for startup
    sleep 10
    
    # Test if dashboard is responding
    if curl -f http://localhost:8501 &> /dev/null; then
        print_success "Dashboard is responding correctly!"
    else
        print_error "Dashboard is not responding"
    fi
    
    # Cleanup
    kill $TEST_PID
    docker rmi $PROJECT_NAME-test
    
    print_success "Test deployment complete"
}

show_help() {
    echo "Tweener Fund Dashboard - Unified Deployment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --local          Deploy locally with Docker"
    echo "  --streamlit-cloud Deploy to Streamlit Community Cloud"
    echo "  --test           Test deployment locally"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --local"
    echo "  $0 --streamlit-cloud"
}

# Main script
main() {
    case "${1:-}" in
        --local)
            check_dependencies
            deploy_local
            ;;
        --streamlit-cloud)
            deploy_streamlit_cloud
            ;;
        --test)
            check_dependencies
            test_deployment
            ;;
        --help|"")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 