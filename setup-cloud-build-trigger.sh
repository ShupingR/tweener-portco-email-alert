#!/bin/bash

# Setup Cloud Build Trigger for CI/CD
# This script creates a Cloud Build trigger that automatically builds and deploys
# the application when changes are pushed to the main branch

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
GITHUB_OWNER="ShupingR"  # Replace with your GitHub username/org
GITHUB_REPO="tweener-portco-email-alert"  # Replace with your repository name
BRANCH="main"
REGION="us-central1"

echo -e "${BLUE}Please update the GitHub owner and repository name in this script before proceeding.${NC}"
echo -e "${BLUE}Current settings:${NC}"
echo -e "  GitHub Owner: ${GITHUB_OWNER}"
echo -e "  GitHub Repo: ${GITHUB_REPO}"
echo -e ""

echo -e "${BLUE}Setting up Cloud Build trigger for CI/CD...${NC}"

# Check if user is authenticated
echo -e "${YELLOW}Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo -e "${RED}Error: Not authenticated with gcloud. Please run 'gcloud auth login'${NC}"
    exit 1
fi

# Set the project
echo -e "${YELLOW}Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project "${PROJECT_ID}"

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet

# Skip repository check as it requires manual connection through console
echo -e "${YELLOW}Note: This script assumes you have already connected your GitHub repository through the Cloud Console.${NC}"
echo -e "${YELLOW}If you haven't, please follow these steps first:${NC}"
echo -e "${BLUE}1. Go to https://console.cloud.google.com/cloud-build/triggers${NC}"
echo -e "${BLUE}2. Click 'Connect Repository'${NC}"
echo -e "${BLUE}3. Follow the GitHub authentication flow${NC}"
echo -e "${BLUE}4. Select your repository and complete the connection${NC}"
echo -e ""
read -p "Have you connected your GitHub repository? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Please connect your repository first, then run this script again.${NC}"
    exit 1
fi

# Create the Cloud Build trigger
echo -e "${YELLOW}Creating Cloud Build trigger...${NC}"

# Check if trigger already exists
if gcloud builds triggers list --filter="name:${TRIGGER_NAME}" --format="value(name)" | grep -q "${TRIGGER_NAME}"; then
    echo -e "${YELLOW}Trigger '${TRIGGER_NAME}' already exists. Updating...${NC}"
    gcloud builds triggers delete "${TRIGGER_NAME}" --quiet
fi

# Create the trigger
gcloud builds triggers create github \
    --name="${TRIGGER_NAME}" \
    --repo-owner="${GITHUB_OWNER}" \
    --repo-name="${GITHUB_REPO}" \
    --branch-pattern="^${BRANCH}$" \
    --build-config="cloudbuild.yaml" \
    --description="Automated build and deploy for Tweener Insights dashboard" \
    --substitutions="_REGION=${REGION}" \
    --include-logs-with-status

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cloud Build trigger created successfully!${NC}"
else
    echo -e "${RED}✗ Failed to create Cloud Build trigger${NC}"
    exit 1
fi

# Grant necessary permissions to Cloud Build service account
echo -e "${YELLOW}Granting permissions to Cloud Build service account...${NC}"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

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

# Display trigger information
echo -e "\n${BLUE}Cloud Build Trigger Information:${NC}"
echo -e "  ${GREEN}Name:${NC} ${TRIGGER_NAME}"
echo -e "  ${GREEN}Repository:${NC} ${GITHUB_OWNER}/${GITHUB_REPO}"
echo -e "  ${GREEN}Branch:${NC} ${BRANCH}"
echo -e "  ${GREEN}Build Config:${NC} cloudbuild.yaml"
echo -e "  ${GREEN}Region:${NC} ${REGION}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "1. Push changes to the '${BRANCH}' branch to trigger a build"
echo -e "2. Monitor builds at: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
echo -e "3. View deployed application at: https://console.cloud.google.com/run?project=${PROJECT_ID}"

echo -e "\n${GREEN}✓ Cloud Build trigger setup complete!${NC}"