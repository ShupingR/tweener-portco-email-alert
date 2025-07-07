#!/bin/bash
# Setup Cloud Scheduler for Automated Email Processing
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
SERVICE_ACCOUNT="email-alert-service@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${BLUE}=== Setting Up Cloud Scheduler for Automated Email Processing ===${NC}"
echo

# Step 1: Enable Cloud Scheduler API
echo -e "${YELLOW}1. Enabling Cloud Scheduler API...${NC}"
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID
echo -e "${GREEN}✅ Cloud Scheduler API enabled${NC}"
echo

# Step 2: Grant Cloud Scheduler permissions to service account
echo -e "${YELLOW}2. Granting Cloud Scheduler permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudscheduler.admin"
echo -e "${GREEN}✅ Cloud Scheduler permissions granted${NC}"
echo

# Step 3: Create the Cloud Scheduler job
echo -e "${YELLOW}3. Creating Cloud Scheduler job...${NC}"
gcloud scheduler jobs create http tweener-email-processor-daily \
    --schedule="0 9 * * *" \
    --time-zone="UTC" \
    --uri="${SERVICE_URL}?action=process_emails&days=7&dry_run=false" \
    --http-method=GET \
    --oidc-service-account-email="${SERVICE_ACCOUNT}" \
    --oidc-token-audience="${SERVICE_URL}" \
    --max-retry-attempts=3 \
    --max-backoff-duration=300s \
    --min-backoff-duration=60s \
    --max-doublings=3 \
    --project=$PROJECT_ID \
    --location=$REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cloud Scheduler job created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create Cloud Scheduler job${NC}"
    exit 1
fi
echo

# Step 4: Test the job
echo -e "${YELLOW}4. Testing the Cloud Scheduler job...${NC}"
gcloud scheduler jobs run tweener-email-processor-daily \
    --project=$PROJECT_ID \
    --location=$REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cloud Scheduler job test successful${NC}"
else
    echo -e "${YELLOW}⚠️ Cloud Scheduler job test failed (this might be expected)${NC}"
fi
echo

# Step 5: Show job details
echo -e "${YELLOW}5. Cloud Scheduler Job Details:${NC}"
gcloud scheduler jobs describe tweener-email-processor-daily \
    --project=$PROJECT_ID \
    --location=$REGION

echo
echo -e "${GREEN}=== Cloud Scheduler Setup Complete ===${NC}"
echo
echo -e "${BLUE}Job Details:${NC}"
echo -e "  Name: tweener-email-processor-daily"
echo -e "  Schedule: Daily at 9:00 AM UTC"
echo -e "  URL: ${SERVICE_URL}?action=process_emails&days=7&dry_run=false"
echo -e "  Service Account: ${SERVICE_ACCOUNT}"
echo
echo -e "${BLUE}Management Commands:${NC}"
echo -e "  View job: gcloud scheduler jobs describe tweener-email-processor-daily --project=$PROJECT_ID --location=$REGION"
echo -e "  Run job: gcloud scheduler jobs run tweener-email-processor-daily --project=$PROJECT_ID --location=$REGION"
echo -e "  Pause job: gcloud scheduler jobs pause tweener-email-processor-daily --project=$PROJECT_ID --location=$REGION"
echo -e "  Resume job: gcloud scheduler jobs resume tweener-email-processor-daily --project=$PROJECT_ID --location=$REGION"
echo -e "  Delete job: gcloud scheduler jobs delete tweener-email-processor-daily --project=$PROJECT_ID --location=$REGION"
echo
echo -e "${GREEN}🎉 Automated email processing is now set up!${NC}"
echo -e "The system will automatically process emails daily at 9:00 AM UTC." 