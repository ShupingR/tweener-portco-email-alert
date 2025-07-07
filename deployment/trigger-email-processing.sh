#!/bin/bash
# Manual Email Processing Trigger
set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="famous-rhythm-465100-p6"
REGION="us-central1"
SERVICE_URL="https://tweener-insights-hsgfqtamea-uc.a.run.app"

echo -e "${BLUE}=== Manual Email Processing Trigger ===${NC}"
echo

# Get parameters
DAYS=${1:-7}
DRY_RUN=${2:-false}

echo -e "${YELLOW}Parameters:${NC}"
echo -e "  Days back: ${DAYS}"
echo -e "  Dry run: ${DRY_RUN}"
echo

# Build URL
PROCESSING_URL="${SERVICE_URL}?action=process_emails&days=${DAYS}&dry_run=${DRY_RUN}"

echo -e "${YELLOW}Triggering email processing...${NC}"
echo -e "URL: ${PROCESSING_URL}"
echo

# Trigger the processing
curl -X GET "${PROCESSING_URL}" \
    -H "Content-Type: application/json" \
    --max-time 300 \
    --connect-timeout 30

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Email processing triggered successfully${NC}"
else
    echo -e "\n${RED}❌ Failed to trigger email processing${NC}"
    exit 1
fi

echo
echo -e "${BLUE}Check the Cloud Run logs for processing details:${NC}"
echo -e "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=tweener-insights' --project=$PROJECT_ID --limit=50" 