#!/bin/bash

echo "🚀 Direct Local Deployment"

# Use a minimal requirements file to avoid build timeouts
if [ -f "requirements-full.txt" ]; then
    echo "Using minimal requirements for faster deployment..."
    cp requirements.txt requirements-current.txt
    cat > requirements.txt << EOF
streamlit==1.46.1
pandas==2.1.3
plotly==6.2.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
anthropic
python-dotenv==1.0.0
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
EOF
fi

# Deploy
echo "Deploying to Cloud Run..."
gcloud run deploy tweener-insights \
    --source . \
    --region us-central1 \
    --port 8501 \
    --memory 1Gi \
    --timeout 600 \
    --allow-unauthenticated \
    --quiet

# Restore original requirements
if [ -f "requirements-current.txt" ]; then
    mv requirements-current.txt requirements.txt
fi

# Get URL
SERVICE_URL=$(gcloud run services describe tweener-insights --region us-central1 --format 'value(status.url)')
echo "✅ Your app should be available at: $SERVICE_URL"