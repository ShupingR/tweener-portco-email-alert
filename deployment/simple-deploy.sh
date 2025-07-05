#!/bin/bash

# Simple Deploy Script for Tweener Insights Dashboard
# No Docker required - uses Google App Engine directly

set -e

# Configuration
PROJECT_ID="portcoupdate"
REGION="us-central1"
SERVICE_NAME="tweener-insights"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Simple Deploy: Tweener Insights Dashboard${NC}"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK is not installed. Please install it first.${NC}"
    echo "macOS: brew install google-cloud-sdk"
    echo "Windows: https://cloud.google.com/sdk/docs/install"
    echo "Linux: curl https://sdk.cloud.google.com | bash"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  You are not authenticated with Google Cloud.${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Get project ID if not set
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo -e "${YELLOW}📋 Please enter your Google Cloud Project ID:${NC}"
    read -p "Project ID: " PROJECT_ID
fi

# Set the project
echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create app.yaml if it doesn't exist
if [ ! -f "app.yaml" ]; then
    echo -e "${RED}❌ app.yaml not found. Please ensure it exists in the current directory.${NC}"
    exit 1
fi

# Deploy to App Engine
echo -e "${YELLOW}🚀 Deploying to Google App Engine...${NC}"
echo -e "${BLUE}This will take a few minutes...${NC}"

gcloud app deploy app.yaml --quiet

# Get the service URL
SERVICE_URL=$(gcloud app browse --no-launch-browser --format="value(url)")

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Your dashboard is available at: $SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}📊 Quick Commands:${NC}"
echo "  View logs: gcloud app logs tail -s default"
echo "  Open dashboard: gcloud app browse"
echo "  Stop service: gcloud app versions stop v1"
echo ""
echo -e "${GREEN}🎉 Simple deployment complete!${NC}" 