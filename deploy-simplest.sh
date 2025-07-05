#!/bin/bash

echo "🚀 Simplest Deployment Method"

# Deploy directly - let Google figure everything out
gcloud run deploy tweener-insights \
    --source . \
    --region us-central1 \
    --allow-unauthenticated

echo "Done! Check above for your app URL"