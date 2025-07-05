#!/bin/bash

echo "🧪 Testing Cloud Run with minimal app..."

# Create a minimal test directory
mkdir -p cloud-run-test
cd cloud-run-test

# Create minimal app
cat > app.py << 'EOF'
import streamlit as st
st.title("Tweener Insights - Test")
st.write("Cloud Run deployment successful!")
EOF

# Create minimal requirements
cat > requirements.txt << 'EOF'
streamlit==1.46.1
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# Deploy
echo "Deploying test app..."
gcloud run deploy tweener-test \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --quiet

cd ..
echo "✅ Test complete"