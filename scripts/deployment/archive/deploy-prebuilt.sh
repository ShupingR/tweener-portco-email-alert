#!/bin/bash

echo "🚀 Deploying with pre-built Streamlit image..."

# Create a custom entrypoint script
cat > entrypoint.sh << 'EOF'
#!/bin/bash
cd /app
pip install -r requirements.txt
streamlit run dashboard/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
EOF

chmod +x entrypoint.sh

# Deploy using a base Streamlit image
gcloud run deploy tweener-insights \
    --image python:3.11-slim \
    --region us-central1 \
    --memory 1Gi \
    --cpu 1 \
    --port 8080 \
    --command="/bin/bash" \
    --args="-c,cd /app && pip install streamlit && streamlit run dashboard/streamlit_app.py --server.port=\$PORT --server.address=0.0.0.0"

echo "✅ Deployment complete!"