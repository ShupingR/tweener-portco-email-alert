# CI/CD Setup with Google Cloud Build

This document describes how to set up continuous integration and deployment (CI/CD) for the Tweener Insights dashboard using Google Cloud Build.

## Overview

The CI/CD pipeline automatically:
1. Builds a Docker container when changes are pushed to the main branch
2. Pushes the container to Google Container Registry
3. Deploys the container to Cloud Run

## Prerequisites

1. Google Cloud Project with billing enabled
2. GitHub repository connected to Cloud Build
3. Following APIs enabled:
   - Cloud Build API
   - Container Registry API
   - Cloud Run API

## Setup Instructions

### 1. Connect GitHub Repository

First, connect your GitHub repository to Cloud Build:

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Connect Repository"
3. Select GitHub and authenticate
4. Choose your repository
5. Complete the connection process

### 2. Run the Setup Script

Execute the provided setup script:

```bash
./setup-cloud-build-trigger.sh
```

This script will:
- Enable required APIs
- Create a Cloud Build trigger
- Set up necessary IAM permissions
- Configure the trigger to run on pushes to main branch

### 3. Verify the Configuration

The `cloudbuild.yaml` file in the repository root defines the build steps:

```yaml
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/tweener-insights:$COMMIT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/tweener-insights:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'tweener-insights'
      - '--image'
      - 'gcr.io/$PROJECT_ID/tweener-insights:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--max-instances'
      - '10'
      - '--timeout'
      - '300'
      - '--set-env-vars'
      - 'GOOGLE_CLOUD_PROJECT=$PROJECT_ID'

images:
  - 'gcr.io/$PROJECT_ID/tweener-insights:$COMMIT_SHA'

timeout: '1200s'
```

## Trigger Configuration

The Cloud Build trigger is configured with:
- **Name**: `tweener-insights-main-trigger`
- **Branch**: `main`
- **Build Config**: `cloudbuild.yaml`
- **Event**: Push to branch

## Environment Variables

The following environment variables are passed to the Cloud Run deployment:
- `GOOGLE_CLOUD_PROJECT`: Set to the project ID automatically

Additional secrets should be configured in Secret Manager and referenced in the deployment.

## Monitoring Builds

### View Build History
```bash
gcloud builds list --limit=10
```

### View Specific Build Logs
```bash
gcloud builds log BUILD_ID
```

### Web Console
Monitor builds at: https://console.cloud.google.com/cloud-build/builds

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Ensure Cloud Build service account has necessary roles:
     - `roles/run.admin`
     - `roles/iam.serviceAccountUser`
     - `roles/storage.admin`

2. **Build Timeouts**
   - Current timeout is set to 20 minutes (1200s)
   - Increase if needed in `cloudbuild.yaml`

3. **Container Registry Issues**
   - Verify Container Registry API is enabled
   - Check project has billing enabled

### Debug Commands

```bash
# Check trigger status
gcloud builds triggers list

# View trigger details
gcloud builds triggers describe tweener-insights-main-trigger

# Test trigger manually
gcloud builds triggers run tweener-insights-main-trigger --branch=main
```

## Security Considerations

1. **Secrets Management**
   - Use Google Secret Manager for sensitive data
   - Never commit secrets to the repository

2. **IAM Permissions**
   - Follow principle of least privilege
   - Regularly audit service account permissions

3. **Container Security**
   - Keep base images updated
   - Scan images for vulnerabilities

## Best Practices

1. **Version Tagging**
   - Images are tagged with commit SHA for traceability
   - Consider adding semantic versioning tags

2. **Build Optimization**
   - Use Docker layer caching
   - Minimize image size
   - Use multi-stage builds when appropriate

3. **Deployment Strategy**
   - Consider implementing blue-green deployments
   - Set up health checks
   - Configure auto-scaling appropriately

## Additional Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)