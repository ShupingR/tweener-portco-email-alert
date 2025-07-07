#!/bin/bash

# Manual steps for setting up Cloud Build trigger
# This script provides the commands to run after GitHub connection is established

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="famous-rhythm-465100-p6"
TRIGGER_NAME="tweener-insights-main-trigger"
REGION="us-central1"

echo -e "${BLUE}=== Cloud Build Trigger Setup Guide ===${NC}"
echo -e ""
echo -e "${YELLOW}STEP 1: Connect GitHub Repository (Manual)${NC}"
echo -e "1. Open: https://console.cloud.google.com/cloud-build/triggers/connect?project=${PROJECT_ID}"
echo -e "2. Select 'GitHub' as the source"
echo -e "3. Authenticate with GitHub"
echo -e "4. Select repository: ShupingR/tweener-portco-email-alert"
echo -e "5. Click 'Connect'"
echo -e ""
read -p "Press Enter after completing Step 1..."

echo -e ""
echo -e "${YELLOW}STEP 2: Create Build Trigger${NC}"
echo -e "After connecting your repository, you can create the trigger manually in the console:"
echo -e ""
echo -e "1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=${PROJECT_ID}"
echo -e "2. Click 'Create Trigger'"
echo -e "3. Configure with these settings:"
echo -e "   - Name: ${TRIGGER_NAME}"
echo -e "   - Event: Push to a branch"
echo -e "   - Source: ShupingR/tweener-portco-email-alert"
echo -e "   - Branch: ^main$"
echo -e "   - Configuration: Cloud Build configuration file"
echo -e "   - Location: /cloudbuild.yaml"
echo -e ""

echo -e "${YELLOW}STEP 3: Grant Permissions${NC}"
echo -e "Run these commands to grant necessary permissions:"
echo -e ""

# Get project number
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo -e "${BLUE}Granting permissions to Cloud Build service account...${NC}"

# Commands to run
echo "gcloud projects add-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member=\"serviceAccount:${CLOUD_BUILD_SA}\" \\"
echo "    --role=\"roles/run.admin\""
echo ""
echo "gcloud projects add-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member=\"serviceAccount:${CLOUD_BUILD_SA}\" \\"
echo "    --role=\"roles/iam.serviceAccountUser\""
echo ""
echo "gcloud projects add-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member=\"serviceAccount:${CLOUD_BUILD_SA}\" \\"
echo "    --role=\"roles/storage.admin\""

echo -e ""
read -p "Do you want to run these permission commands now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Grant Cloud Run Admin permission
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="roles/run.admin" \
        --quiet

    # Grant Service Account User permission
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="roles/iam.serviceAccountUser" \
        --quiet

    # Grant Container Registry permissions
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="roles/storage.admin" \
        --quiet

    echo -e "${GREEN}✓ Permissions granted successfully!${NC}"
fi

echo -e ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo -e ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Push changes to the 'main' branch to trigger a build"
echo -e "2. Monitor builds at: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
echo -e "3. View deployed app at: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo -e ""
echo -e "${YELLOW}Test your trigger:${NC}"
echo -e "git add ."
echo -e "git commit -m \"Test Cloud Build trigger\""
echo -e "git push origin main"