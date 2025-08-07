# Closed Book QA - GCP FastAPI Deployment

This directory contains the Google Cloud Platform (GCP) deployment configuration for the Closed Book QA application using FastAPI.

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud SDK**: Install and configure gcloud CLI
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Authenticate
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Set Environment Variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

### Deployment Options

#### Option 1: Automated Deployment (Recommended)
```bash
./deploy-gcp.sh
```

#### Option 2: Manual Cloud Run Deployment
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/closed-book-qa
gcloud run deploy closed-book-qa \
    --image gcr.io/$PROJECT_ID/closed-book-qa \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY"
```

#### Option 3: App Engine Deployment
```bash
# Update app.yaml with your API key
sed -i "s/your-google-api-key-here/$GOOGLE_API_KEY/g" app.yaml
gcloud app deploy app.yaml
```

## 📁 File Structure

```
├── src/
│   ├── fastapi_app.py          # FastAPI backend application
│   └── streamlit_gcp_frontend.py # Streamlit frontend for GCP
├── Dockerfile.gcp              # Docker configuration for GCP
├── requirements-gcp.txt        # Python dependencies for GCP
├── cloudbuild.yaml            # Google Cloud Build configuration
├── app.yaml                   # App Engine configuration
├── deploy-gcp.sh             # Automated deployment script
└── README-GCP.md             # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key | Yes |
| `PORT` | Server port (default: 8080) | No |
| `API_URL` | Frontend API URL | No |

### Resource Allocation

| Service | CPU | Memory | Timeout | Concurrency |
|---------|-----|--------|---------|-------------|
| Cloud Run | 2 | 2Gi | 300s | 80 |
| App Engine | 2 | 2Gi | 300s | 80 |
| Compute Engine | 2 | 8Gi | N/A | N/A |

## 🌐 API Endpoints

### Health Check
```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "vector_stores_loaded": ["debt_crisis", "capitalism"],
  "embeddings_model_loaded": true
}
```

### Ask Question
```bash
POST /api/ask
Content-Type: application/json

{
  "question": "What is a debt crisis?",
  "book_id": "debt_crisis"
}
```

Response:
```json
{
  "answer": "A debt crisis occurs when...",
  "sources": [
    {
      "content": "Source text...",
      "metadata": {
        "chapter": "Chapter 1",
        "pdf_page": 15,
        "book_id": "debt_crisis"
      },
      "rank": 1
    }
  ],
  "processing_time": 2.45,
  "status": "success"
}
```

### Available Books
```bash
GET /api/books
```

Response:
```json
{
  "books": [
    {
      "id": "debt_crisis",
      "name": "Big Debt Crisis by Ray Dalio",
      "description": "Analysis of debt crises throughout history"
    },
    {
      "id": "capitalism",
      "name": "Saving Capitalism from the Capitalists",
      "description": "Analysis of financial markets and capitalism"
    }
  ]
}
```

## 🔍 Monitoring

### Cloud Run Monitoring
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=closed-book-qa"

# View metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

### App Engine Monitoring
```bash
# View logs
gcloud app logs tail -s default

# View instances
gcloud app instances list
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Issues**:
   ```bash
   # Verify API key is set
   echo $GOOGLE_API_KEY
   
   # Test API key
   curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
        https://generativelanguage.googleapis.com/v1beta/models
   ```

2. **Vector Store Loading Issues**:
   ```bash
   # Check if vector stores exist
   ls -la vector_store/
   
   # Re-run ingestion if needed
   python src/data_ingestion.py
   ```

3. **Memory Issues**:
   - Increase memory allocation in deployment configuration
   - Check for memory leaks in the application
   - Monitor resource usage in Cloud Console

4. **Timeout Issues**:
   - Increase timeout in deployment configuration
   - Optimize RAG pipeline performance
   - Use async operations where possible

### Debug Commands

```bash
# Test API locally
uvicorn src.fastapi_app:app --host 0.0.0.0 --port 8080

# Test with curl
curl -X POST "http://localhost:8080/api/ask" \
     -H "Content-Type: application/json" \
     -d '{"question":"test","book_id":"debt_crisis"}'

# Check container logs
gcloud run services logs read closed-book-qa
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Build new image
gcloud builds submit --tag gcr.io/$PROJECT_ID/closed-book-qa

# Deploy update
gcloud run deploy closed-book-qa \
    --image gcr.io/$PROJECT_ID/closed-book-qa \
    --region us-central1
```

### Scaling
```bash
# Scale up
gcloud run services update closed-book-qa \
    --max-instances 20 \
    --concurrency 100

# Scale down
gcloud run services update closed-book-qa \
    --max-instances 5 \
    --concurrency 50
```

## 💰 Cost Optimization

### Cloud Run Cost Optimization
- Use appropriate memory allocation (2Gi is usually sufficient)
- Set max instances to limit costs
- Use concurrency to optimize resource usage
- Monitor usage in Cloud Console

### App Engine Cost Optimization
- Use automatic scaling with appropriate targets
- Set min and max instances appropriately
- Monitor instance hours and requests

## 🔐 Security

### Best Practices
1. Store API keys in environment variables
2. Use IAM roles for service accounts
3. Enable audit logging
4. Use HTTPS for all communications
5. Implement rate limiting if needed

### IAM Setup
```bash
# Create service account
gcloud iam service-accounts create closed-book-qa-sa \
    --display-name="Closed Book QA Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:closed-book-qa-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

## 📊 Performance Optimization

### FastAPI Optimizations
- Use async/await for I/O operations
- Implement proper caching
- Use connection pooling
- Optimize database queries

### RAG Pipeline Optimizations
- Cache vector stores in memory
- Use efficient embedding models
- Implement proper chunking strategies
- Optimize retrieval algorithms

## 🆘 Support

For issues and support:
- Check Cloud Console logs
- Review application logs
- Test endpoints individually
- Verify environment variables
- Check resource allocation

## 📝 Notes

- The FastAPI backend is optimized for GCP deployment
- Vector stores are pre-loaded on startup for better performance
- Async operations are used throughout for better scalability
- Health checks are implemented for monitoring
- Error handling is comprehensive for production use 