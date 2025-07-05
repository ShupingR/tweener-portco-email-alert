#!/bin/bash
"""
Tweener Fund Dashboard - Unified Deployment Script

This script consolidates all deployment options into a single, clear interface.
Replaces multiple confusing deployment scripts.

Usage:
    ./scripts/deployment/deploy.sh [options]

Options:
    --local          Deploy locally with Docker
    --cloud-run      Deploy to Google Cloud Run
    --heroku         Deploy to Heroku
    --test           Test deployment locally
    --help           Show this help message

Examples:
    ./scripts/deployment/deploy.sh --local
    ./scripts/deployment/deploy.sh --cloud-run
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
REGION="us-central1"
SERVICE_NAME="tweener-fund-dashboard"

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
    
    if ! command -v gcloud &> /dev/null; then
        print_warning "Google Cloud CLI not found (needed for cloud deployment)"
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

deploy_cloud_run() {
    print_header "Deploying to Google Cloud Run"
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI required for cloud deployment"
        exit 1
    fi
    
    # Build and push to Container Registry
    print_header "Building and Pushing Image"
    gcloud builds submit --tag gcr.io/$PROJECT_NAME/$SERVICE_NAME .
    
    # Deploy to Cloud Run
    print_header "Deploying to Cloud Run"
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_NAME/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8501
    
    print_success "Dashboard deployed to Cloud Run!"
}

deploy_heroku() {
    print_header "Deploying to Heroku"
    
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI required for Heroku deployment"
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    if ! heroku apps:info $PROJECT_NAME &> /dev/null; then
        heroku create $PROJECT_NAME
    fi
    
    # Deploy
    git push heroku main
    
    print_success "Dashboard deployed to Heroku!"
    echo "Access at: https://$PROJECT_NAME.herokuapp.com"
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
    echo "  --cloud-run      Deploy to Google Cloud Run"
    echo "  --heroku         Deploy to Heroku"
    echo "  --test           Test deployment locally"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --local"
    echo "  $0 --cloud-run"
}

# Main script
main() {
    case "${1:-}" in
        --local)
            check_dependencies
            deploy_local
            ;;
        --cloud-run)
            check_dependencies
            deploy_cloud_run
            ;;
        --heroku)
            check_dependencies
            deploy_heroku
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

main "$@" 