#!/bin/bash

# GCP Deployment Script for Closed Book QA
# This script deploys a single-container application (FastAPI + Streamlit)
# to Google Cloud Run.

set -e

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
REGION="europe-west1"
SERVICE_NAME="closedbook-qa"

# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper Functions ---
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${YELLOW}⚠️ You are not authenticated with gcloud. Please run 'gcloud auth login'.${NC}"
        exit 1
    fi
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}⚠️ No project ID set. Please set it with 'gcloud config set project YOUR_PROJECT_ID'.${NC}"
        exit 1
    fi
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo -e "${YELLOW}⚠️ GOOGLE_API_KEY environment variable is not set.${NC}"
        read -p "Enter your Google API Key: " GOOGLE_API_KEY
        export GOOGLE_API_KEY
    fi
}

deploy_cloud_run() {
    echo -e "${GREEN}📦 Building and deploying service: ${SERVICE_NAME}${NC}"
    
    # Build and push the container using the main Dockerfile
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --file Dockerfile
    
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
        
    echo -e "${GREEN}✅ Deployment complete!${NC}"
}

# --- Main Execution ---
echo -e "${GREEN}🚀 GCP Cloud Run Deployment Script${NC}"
echo "========================================"
check_gcloud

echo -e "${YELLOW}This will deploy the combined service: ${SERVICE_NAME}${NC}"
read -p "Do you want to proceed? (y/N): " choice

if [[ "$choice" =~ ^[Yy]$ ]]; then
    deploy_cloud_run
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${YELLOW}➡️ Access your application at: ${SERVICE_URL}${NC}"
else
    echo -e "${RED}Deployment cancelled.${NC}"
fi 