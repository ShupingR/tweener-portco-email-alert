# Google Cloud Run Deployment

This directory contains all files needed for deploying the Tweener Fund Portfolio Intelligence Platform to Google Cloud Run.

## Files

- **`Dockerfile`** - Container configuration for the Streamlit application
- **`cloudbuild.yaml`** - CI/CD pipeline configuration for automated builds
- **`deploy-gcp.sh`** - Manual deployment script
- **`.gcloudignore`** - Excludes unnecessary files from Google Cloud uploads
- **`.dockerignore`** - Excludes unnecessary files from Docker builds

## Quick Deployment

```bash
# Deploy to Google Cloud Run
bash deployment/deploy-gcp.sh
```

## CI/CD Pipeline

The application uses Google Cloud Build for automated deployment:

1. **Trigger**: Every push to the `main` branch
2. **Build**: Docker container with Streamlit app
3. **Deploy**: To Cloud Run service `tweener-insights`
4. **URL**: `https://tweener-insights-hsgfqtamea-uc.a.run.app`

## Manual Deployment

```bash
# Build Docker image
docker build -f deployment/Dockerfile -t gcr.io/PROJECT_ID/SERVICE_NAME .

# Push to Container Registry
docker push gcr.io/PROJECT_ID/SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy SERVICE_NAME \
  --image gcr.io/PROJECT_ID/SERVICE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

The deployment uses Google Cloud Secret Manager for sensitive data:
- `ADMIN_PASSWORD`
- `ANTHROPIC_API_KEY`
- `DATABASE_URL`
- `GMAIL_PASSWORD`
- `GMAIL_USERNAME`
- `GP_EMAILS`
- `SESSION_SECRET`
- `USER_CREDENTIALS`

## Service Configuration

- **Memory**: 2Gi
- **CPU**: 2 cores
- **Max Instances**: 10
- **Timeout**: 300 seconds
- **Port**: 8080 