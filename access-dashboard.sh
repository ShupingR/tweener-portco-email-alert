#!/bin/bash

# SummerAI Dashboard Authenticated Access
# This script creates a local proxy with authentication to access your Cloud Run service

PROJECT_ID="famous-rhythm-465100-p6"
SERVICE_NAME="email-alert-dashboard"
REGION="us-east1"
LOCAL_PORT=8081

echo "🔐 SummerAI Dashboard - Authenticated Access"
echo "📊 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔧 Service: $SERVICE_NAME"
echo "🌐 Local Port: $LOCAL_PORT"
echo "=========================================="

# Check if user is authenticated
echo "🔍 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "shuping@summerai.biz"; then
    echo "❌ You need to authenticate first:"
    echo "gcloud auth login shuping@summerai.biz"
    exit 1
fi

echo "✅ Authentication verified!"
echo ""

# Start the authenticated proxy
echo "🚀 Starting authenticated proxy..."
echo "📱 Your dashboard will be available at: http://localhost:$LOCAL_PORT"
echo "🔑 Dashboard password: TweenerAdmin2025"
echo ""
echo "💡 The proxy will handle Google Cloud authentication automatically."
echo "   Just use the dashboard password when prompted."
echo ""
echo "🛑 Press Ctrl+C to stop the proxy when done."
echo "=========================================="

# Start the proxy with proper authentication
gcloud run services proxy $SERVICE_NAME --port=$LOCAL_PORT --region=$REGION

echo ""
echo "👋 Proxy stopped. Dashboard is no longer accessible."
