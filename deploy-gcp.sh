#!/bin/bash

# GCP Deployment Script for Closed Book QA
# This script provides multiple deployment options for Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
REGION="us-central1"
SERVICE_NAME="closed-book-qa"

echo -e "${GREEN}🚀 GCP Deployment Script for Closed Book QA${NC}"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  You are not authenticated with gcloud. Please run:${NC}"
    echo "gcloud auth login"
    exit 1
fi

# Set project if not set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  No project ID set. Please set it with:${NC}"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"

# Function to deploy to Cloud Run
deploy_cloud_run() {
    echo -e "${GREEN}📦 Deploying to Cloud Run...${NC}"
    
    # Build and push the container
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
    
    # Deploy to Cloud Run
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --concurrency 80 \
        --max-instances 10 \
        --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY"
    
    echo -e "${GREEN}✅ Cloud Run deployment complete!${NC}"
}

# Function to deploy to App Engine
deploy_app_engine() {
    echo -e "${GREEN}📦 Deploying to App Engine...${NC}"
    
    # Update app.yaml with the correct API key
    sed -i.bak "s/your-google-api-key-here/$GOOGLE_API_KEY/g" app.yaml
    
    # Deploy to App Engine
    gcloud app deploy app.yaml --quiet
    
    echo -e "${GREEN}✅ App Engine deployment complete!${NC}"
}

# Function to deploy to Compute Engine
deploy_compute_engine() {
    echo -e "${GREEN}📦 Deploying to Compute Engine...${NC}"
    
    # Create a startup script
    cat > startup-script.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y docker.io
systemctl start docker
systemctl enable docker

# Pull and run the container
docker pull gcr.io/PROJECT_ID/closed-book-qa
docker run -d -p 80:8080 \
    -e GOOGLE_API_KEY="GOOGLE_API_KEY" \
    gcr.io/PROJECT_ID/closed-book-qa
EOF
    
    # Replace placeholders in startup script
    sed -i "s/PROJECT_ID/$PROJECT_ID/g" startup-script.sh
    sed -i "s/GOOGLE_API_KEY/$GOOGLE_API_KEY/g" startup-script.sh
    
    # Create instance
    gcloud compute instances create $SERVICE_NAME \
        --zone=$REGION-a \
        --machine-type=e2-standard-2 \
        --image-family=debian-11 \
        --image-project=debian-cloud \
        --metadata-from-file startup-script=startup-script.sh \
        --tags=http-server,https-server
    
    # Create firewall rule
    gcloud compute firewall-rules create allow-http \
        --allow tcp:80 \
        --target-tags=http-server \
        --source-ranges=0.0.0.0/0
    
    echo -e "${GREEN}✅ Compute Engine deployment complete!${NC}"
}

# Main deployment menu
echo -e "${YELLOW}Choose deployment option:${NC}"
echo "1) Cloud Run (Recommended - Serverless)"
echo "2) App Engine (Serverless)"
echo "3) Compute Engine (VM-based)"
echo "4) All three options"

read -p "Enter your choice (1-4): " choice

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY environment variable is not set.${NC}"
    read -p "Enter your Google API Key: " GOOGLE_API_KEY
    export GOOGLE_API_KEY
fi

case $choice in
    1)
        deploy_cloud_run
        ;;
    2)
        deploy_app_engine
        ;;
    3)
        deploy_compute_engine
        ;;
    4)
        echo -e "${GREEN}🚀 Deploying to all three platforms...${NC}"
        deploy_cloud_run
        echo ""
        deploy_app_engine
        echo ""
        deploy_compute_engine
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your Streamlit frontend with the new API URL"
echo "2. Test the API endpoints"
echo "3. Monitor the deployment in Google Cloud Console"
echo ""
echo -e "${GREEN}API Endpoints:${NC}"
echo "- Health check: https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app/api/health"
echo "- Ask question: https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app/api/ask"
echo "- Available books: https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app/api/books" 