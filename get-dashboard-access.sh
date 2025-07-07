#!/bin/bash

# SummerAI Dashboard Access Script
# This script provides authenticated access to your Cloud Run service

PROJECT_ID="famous-rhythm-465100-p6"
SERVICE_NAME="email-alert-dashboard"
REGION="us-east1"
SERVICE_URL="https://email-alert-dashboard-1025413634484.us-east1.run.app"

echo "🔐 Getting authenticated access to SummerAI Dashboard"
echo "📊 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔧 Service: $SERVICE_NAME"
echo "=========================================="

# Method 1: Generate an identity token for direct access
echo "🎫 Generating identity token..."
TOKEN=$(gcloud auth print-identity-token)

if [ $? -eq 0 ]; then
    echo "✅ Token generated successfully!"
    echo ""
    echo "🌐 You can access your dashboard using one of these methods:"
    echo ""
    echo "Method 1: Using curl with authentication"
    echo "curl -H \"Authorization: Bearer $TOKEN\" $SERVICE_URL"
    echo ""
    echo "Method 2: Copy this authenticated URL to your browser:"
    echo "$SERVICE_URL"
    echo ""
    echo "💡 Since the application now has built-in authentication, you can:"
    echo "1. Visit: $SERVICE_URL"
    echo "2. Enter your admin password: TweenerAdmin2025"
    echo "3. Access your dashboard!"
    echo ""
else
    echo "❌ Failed to generate token. Make sure you're authenticated with:"
    echo "gcloud auth login shuping@summerai.biz"
fi

# Method 3: Try to open in browser with authentication
echo "🚀 Attempting to access dashboard with authentication..."
echo "If browser doesn't open automatically, use the curl command above or:"
echo "1. Make sure you're logged in: gcloud auth login shuping@summerai.biz"
echo "2. Get a new token: gcloud auth print-identity-token"
echo "3. Use the token in Authorization header when visiting: $SERVICE_URL"
echo ""
echo "Or try this authenticated curl request:"
echo "curl -H \"Authorization: Bearer $TOKEN\" $SERVICE_URL"
echo ""
echo "💡 Dashboard password once you get through: TweenerAdmin2025"
