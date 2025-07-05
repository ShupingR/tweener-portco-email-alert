# Tweener Insights Dashboard - Google Cloud Deployment Guide

This guide will help you deploy your Streamlit dashboard to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud SDK**: Install the Google Cloud CLI
3. **Docker**: Install Docker Desktop or Docker Engine
4. **Git**: For version control (optional but recommended)

## Step 1: Install Google Cloud SDK

### macOS (using Homebrew):
```bash
brew install google-cloud-sdk
```

### Windows:
Download and install from: https://cloud.google.com/sdk/docs/install

### Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## Step 2: Set Up Google Cloud Project

1. **Create a new project** (or use existing):
   ```bash
   gcloud projects create tweener-insights-dashboard --name="Tweener Insights Dashboard"
   ```

2. **Set the project as default**:
   ```bash
   gcloud config set project tweener-insights-dashboard
   ```

3. **Enable billing** for your project in the Google Cloud Console

4. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   ```

## Step 3: Configure the Deployment

1. **Update the project ID** in `deploy.sh`:
   ```bash
   # Edit deploy.sh and replace "your-gcp-project-id" with your actual project ID
   PROJECT_ID="tweener-insights-dashboard"  # Your actual project ID
   ```

2. **Set up environment variables** (if needed):
   - Create a `.env` file with your database credentials
   - Update the Dockerfile to copy the `.env` file if needed

## Step 4: Deploy to Google Cloud

### Quick Deploy (Simplest)
```bash
# Deploy using the simple deployment script
bash deployment/simple-deploy.sh
```

### Option A: Using the Deployment Script (Recommended)

1. **Make the script executable** (already done):
   ```bash
   chmod +x deploy.sh
   ```

2. **Run the deployment**:
   ```bash
   ./deploy.sh
   ```

### Option B: Manual Deployment

1. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and push the Docker image**:
   ```bash
   PROJECT_ID="your-project-id"
   docker build -t gcr.io/$PROJECT_ID/tweener-insights .
   docker push gcr.io/$PROJECT_ID/tweener-insights
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy tweener-insights \
       --image gcr.io/$PROJECT_ID/tweener-insights \
       --region us-central1 \
       --platform managed \
       --allow-unauthenticated \
       --memory 2Gi \
       --cpu 1 \
       --max-instances 10 \
       --port 8080
   ```

## Step 5: Access Your Dashboard

After successful deployment, you'll get a URL like:
```
https://tweener-insights-xxxxx-uc.a.run.app
```

## Step 6: Set Up Continuous Deployment (Optional)

### Using Cloud Build Triggers

1. **Connect your repository** to Cloud Build
2. **Create a trigger** that builds and deploys on push to main branch
3. **Use the provided `cloudbuild.yaml`** for automated deployments

### Manual Trigger
```bash
gcloud builds submit --config cloudbuild.yaml .
```

## Configuration Options

### Environment Variables

You can set environment variables during deployment:

```bash
gcloud run deploy tweener-insights \
    --image gcr.io/$PROJECT_ID/tweener-insights \
    --set-env-vars "DATABASE_URL=your-database-url" \
    --set-env-vars "API_KEY=your-api-key"
```

### Scaling Configuration

- **Memory**: 2Gi (can be adjusted)
- **CPU**: 1 (can be adjusted)
- **Max Instances**: 10 (can be adjusted)
- **Min Instances**: 0 (for cost optimization)

### Custom Domain (Optional)

To use a custom domain:

1. **Verify domain ownership** in Google Cloud Console
2. **Map the domain**:
   ```bash
   gcloud run domain-mappings create \
       --service tweener-insights \
       --domain your-domain.com \
       --region us-central1
   ```

## Monitoring and Logs

### View Logs
```bash
gcloud logs read --service=tweener-insights --limit=50
```

### Monitor Performance
- Use Google Cloud Console > Cloud Run > tweener-insights
- Set up alerts for errors and performance metrics

## Cost Optimization

### Recommendations:
1. **Set min instances to 0** for cost savings
2. **Use appropriate memory/CPU** for your workload
3. **Monitor usage** and adjust resources as needed
4. **Set up billing alerts** to avoid unexpected charges

### Estimated Costs (us-central1):
- **2Gi memory, 1 CPU**: ~$0.00002400 per 100ms
- **With 0 min instances**: Pay only when used
- **Typical monthly cost**: $10-50 depending on usage

## Troubleshooting

### Common Issues:

1. **Build fails**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Check .dockerignore file

2. **Deployment fails**:
   - Verify project ID is correct
   - Check billing is enabled
   - Ensure APIs are enabled

3. **App doesn't start**:
   - Check logs: `gcloud logs read --service=tweener-insights`
   - Verify environment variables
   - Check port configuration

4. **Database connection issues**:
   - Ensure database is accessible from Cloud Run
   - Check firewall rules
   - Verify connection strings

### Useful Commands:

```bash
# View service details
gcloud run services describe tweener-insights --region=us-central1

# Update service
gcloud run services update tweener-insights --region=us-central1

# Delete service
gcloud run services delete tweener-insights --region=us-central1

# View recent logs
gcloud logs read --service=tweener-insights --limit=20
```

## Security Considerations

1. **Environment Variables**: Store secrets in Secret Manager
2. **HTTPS**: Cloud Run provides HTTPS by default
3. **Access Control**: Dashboard is accessible without authentication
4. **Database**: Use Cloud SQL or secure external database

## Next Steps

1. **Set up monitoring** and alerting
2. **Configure custom domain** (if needed)
3. **Set up CI/CD** pipeline
4. **Configure access control** (if needed)
5. **Optimize performance** based on usage patterns

## Support

For issues with:
- **Google Cloud**: Check Google Cloud documentation
- **Streamlit**: Check Streamlit documentation
- **This application**: Check the project README.md

---

**Note**: This deployment uses Cloud Run, which is serverless and scales to zero when not in use, making it cost-effective for most use cases. 