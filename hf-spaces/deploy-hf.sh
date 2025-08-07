#!/bin/bash

# Hugging Face Spaces Deployment Script for Closed Book QA
# This script helps deploy the application to Hugging Face Spaces

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Hugging Face Spaces Deployment Script for Closed Book QA${NC}"
echo "=========================================================="

# Check if huggingface_hub is installed
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  huggingface_hub is not installed. Installing...${NC}"
    pip install huggingface_hub
fi

# Check if user is authenticated
if ! huggingface-cli whoami &>/dev/null; then
    echo -e "${YELLOW}⚠️  You are not authenticated with Hugging Face. Please run:${NC}"
    echo "huggingface-cli login"
    exit 1
fi

# Get username
USERNAME=$(huggingface-cli whoami)
echo -e "${GREEN}✅ Authenticated as: $USERNAME${NC}"

# Configuration
SPACE_NAME="closed-book-qa"
SPACE_TYPE="streamlit"
LICENSE="mit"

echo -e "${YELLOW}Choose deployment option:${NC}"
echo "1) Create new space"
echo "2) Update existing space"
echo "3) Deploy with custom settings"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}📦 Creating new Hugging Face Space...${NC}"
        
        # Create the space
        huggingface-cli repo create $SPACE_NAME --type space --space-sdk $SPACE_TYPE --license $LICENSE
        
        echo -e "${GREEN}✅ Space created successfully!${NC}"
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Clone the space: git clone https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
        echo "2. Copy your files to the space directory"
        echo "3. Push the changes: git add . && git commit -m 'Initial commit' && git push"
        ;;
        
    2)
        echo -e "${GREEN}📦 Updating existing space...${NC}"
        
        # Check if space exists
        if ! huggingface-cli repo info $USERNAME/$SPACE_NAME &>/dev/null; then
            echo -e "${RED}❌ Space $SPACE_NAME does not exist. Please create it first.${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Space found. Ready for updates.${NC}"
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Clone the space: git clone https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
        echo "2. Copy your updated files to the space directory"
        echo "3. Push the changes: git add . && git commit -m 'Update' && git push"
        ;;
        
    3)
        echo -e "${GREEN}📦 Deploying with custom settings...${NC}"
        
        read -p "Enter space name (default: closed-book-qa): " custom_space_name
        SPACE_NAME=${custom_space_name:-closed-book-qa}
        
        read -p "Enter space SDK (default: streamlit): " custom_sdk
        SPACE_TYPE=${custom_sdk:-streamlit}
        
        read -p "Enter license (default: mit): " custom_license
        LICENSE=${custom_license:-mit}
        
        echo -e "${GREEN}📦 Creating space with custom settings...${NC}"
        echo "Space name: $SPACE_NAME"
        echo "SDK: $SPACE_TYPE"
        echo "License: $LICENSE"
        
        huggingface-cli repo create $SPACE_NAME --type space --space-sdk $SPACE_TYPE --license $LICENSE
        
        echo -e "${GREEN}✅ Custom space created successfully!${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment setup completed!${NC}"
echo ""
echo -e "${YELLOW}Manual deployment steps:${NC}"
echo "1. Clone your space:"
echo "   git clone https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
echo ""
echo "2. Copy these files to the space directory:"
echo "   - app.py (Streamlit frontend)"
echo "   - api.py (FastAPI backend)"
echo "   - requirements.txt"
echo "   - README.md"
echo "   - src/ (your RAG code)"
echo "   - vector_store/ (your vector stores)"
echo ""
echo "3. Set environment variables in HF Spaces settings:"
echo "   - GOOGLE_API_KEY=your_google_api_key"
echo "   - API_URL=http://localhost:8000"
echo ""
echo "4. Push your changes:"
echo "   git add ."
echo "   git commit -m 'Initial deployment'"
echo "   git push"
echo ""
echo -e "${GREEN}Your space will be available at:${NC}"
echo "https://huggingface.co/spaces/$USERNAME/$SPACE_NAME" 