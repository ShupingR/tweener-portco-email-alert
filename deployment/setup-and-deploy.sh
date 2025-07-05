#!/bin/bash

# Setup and Deploy Script for Tweener Insights Dashboard
# Handles permissions and initial setup

set -e

# Configuration
PROJECT_ID="portcoupdate"
REGION="us-central1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setup & Deploy: Tweener Insights Dashboard${NC}"
echo "=================================================="

# Set the project
echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com

# Create App Engine app if it doesn't exist
echo -e "${YELLOW}🏗️  Creating App Engine app (if needed)...${NC}"
gcloud app create --region=$REGION || echo "App Engine app already exists"

# Grant Cloud Build permissions to App Engine service account
echo -e "${YELLOW}🔑 Setting up permissions...${NC}"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

# Grant storage admin permission to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.admin" \
    --quiet

# Also grant cloud build service account permissions
BUILD_SERVICE_ACCOUNT="${PROJECT_ID}@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_SERVICE_ACCOUNT}" \
    --role="roles/storage.admin" \
    --quiet

echo -e "${YELLOW}⏳ Waiting for permissions to propagate...${NC}"
sleep 10

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
echo "  Check status: gcloud app services list"
echo ""
echo -e "${GREEN}🎉 Setup and deployment complete!${NC}"