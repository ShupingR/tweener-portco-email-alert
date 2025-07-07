#!/bin/bash

# Update Cloud Run service with environment variables from Secret Manager

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="famous-rhythm-465100-p6"
SERVICE_NAME="tweener-insights"
REGION="us-central1"

echo -e "${BLUE}Updating Cloud Run service with environment variables...${NC}"

# Update the service with all necessary environment variables
gcloud run services update ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-secrets="ADMIN_PASSWORD=ADMIN_PASSWORD:latest" \
    --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest" \
    --set-secrets="DATABASE_URL=DATABASE_URL:latest" \
    --set-secrets="GMAIL_PASSWORD=GMAIL_PASSWORD:latest" \
    --set-secrets="GMAIL_USERNAME=GMAIL_USERNAME:latest" \
    --set-secrets="GP_EMAILS=GP_EMAILS:latest" \
    --set-secrets="SESSION_SECRET=SESSION_SECRET:latest" \
    --set-secrets="USER_CREDENTIALS=USER_CREDENTIALS:latest" \
    --service-account="email-alert-service@${PROJECT_ID}.iam.gserviceaccount.com"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cloud Run service updated successfully!${NC}"
    echo -e ""
    echo -e "${BLUE}Service URL:${NC}"
    gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --format="value(status.url)"
else
    echo -e "${RED}✗ Failed to update Cloud Run service${NC}"
    exit 1
fi

echo -e ""
echo -e "${YELLOW}Note: The service may take a few moments to redeploy with the new configuration.${NC}"