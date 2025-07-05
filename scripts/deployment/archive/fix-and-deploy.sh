#!/bin/bash

# Fix permissions and deploy to Cloud Run

set -e

PROJECT_ID="portcoupdate"
PROJECT_NUMBER="689379371277"
REGION="us-central1"
SERVICE_NAME="tweener-insights"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 Fixing permissions and deploying${NC}"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Grant storage permissions to Cloud Build service account
echo -e "${YELLOW}Setting up Cloud Build permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin"

# Grant storage permissions to Compute Engine default service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=$REGION \
    --quiet || echo "Repository already exists"

echo -e "${YELLOW}Waiting for permissions to propagate...${NC}"
sleep 10

# Deploy using Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 60 \
    --max-instances 3 \
    --quiet \
    --command "streamlit" \
    --args "run,dashboard/streamlit_app.py,--server.port=8501,--server.address=0.0.0.0"

# Get URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Your app is at: $SERVICE_URL${NC}"