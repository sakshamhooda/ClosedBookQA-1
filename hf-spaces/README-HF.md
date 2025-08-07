# Closed Book QA - Hugging Face Spaces Deployment

This directory contains the Hugging Face Spaces deployment configuration for the Closed Book QA application using Streamlit.

## 🚀 Quick Start

### Prerequisites

1. **Hugging Face Account**: Create an account at [huggingface.co](https://huggingface.co)
2. **HF CLI**: Install and authenticate with Hugging Face CLI
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

3. **Set Environment Variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

### Deployment Options

#### Option 1: Automated Deployment (Recommended)
```bash
cd hf-spaces
./deploy-hf.sh
```

#### Option 2: Manual Web Interface Deployment
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose settings:
   - **Owner**: Your username
   - **Space name**: `closed-book-qa`
   - **License**: MIT
   - **SDK**: Streamlit
   - **Python version**: 3.11

4. Upload your files:
   - `app.py` (Streamlit frontend)
   - `api.py` (FastAPI backend)
   - `requirements.txt` (dependencies)
   - `README.md` (space description)
   - `src/` folder (your RAG code)
   - `vector_store/` folder (your vector stores)

5. Configure environment variables in the HF Spaces settings

#### Option 3: GitHub Integration
1. Push your code to GitHub
2. Connect HF Spaces to your GitHub repo
3. Enable automatic deployments

## 📁 File Structure

```
hf-spaces/
├── app.py                    # Streamlit frontend for HF Spaces
├── api.py                    # FastAPI backend
├── requirements.txt          # Python dependencies
├── README.md                # HF Spaces configuration
├── Dockerfile               # Docker configuration
├── deploy-hf.sh            # Automated deployment script
└── README-HF.md            # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key | Yes |
| `API_URL` | Backend API URL | No (defaults to localhost) |

### HF Spaces Settings

| Setting | Value |
|---------|-------|
| **SDK** | Streamlit |
| **Python Version** | 3.11 |
| **Hardware** | CPU (free) / GPU (paid) |
| **Memory** | 16GB (free) / 32GB (paid) |

## 🌐 Application Features

### Frontend (Streamlit)
- **Book Selection**: Choose between two financial books
- **Chat Interface**: Interactive Q&A with chat history
- **Source Citations**: View source passages with metadata
- **Progress Indicators**: Real-time feedback during processing
- **Error Handling**: Comprehensive error messages

### Backend (FastAPI)
- **Async Operations**: Non-blocking request handling
- **Caching**: Vector stores and embeddings cached in memory
- **Health Checks**: Monitor application status
- **Error Handling**: Graceful error responses

## 🔍 API Endpoints

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

### HF Spaces Monitoring
- **Logs**: Available in the HF Spaces interface
- **Metrics**: Built-in performance monitoring
- **Status**: Real-time application status

### Local Testing
```bash
# Test Streamlit frontend
streamlit run app.py

# Test FastAPI backend
uvicorn api:app --host 0.0.0.0 --port 8000

# Test API endpoints
curl -X POST "http://localhost:8000/api/ask" \
     -H "Content-Type: application/json" \
     -d '{"question":"test","book_id":"debt_crisis"}'
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
   - Upgrade to paid HF Spaces for more memory
   - Optimize vector store loading
   - Use smaller chunk sizes

4. **Timeout Issues**:
   - Increase timeout settings
   - Optimize RAG pipeline performance
   - Use async operations

### Debug Commands

```bash
# Check HF CLI status
huggingface-cli whoami

# List your spaces
huggingface-cli repo list --type space

# Clone a space
git clone https://huggingface.co/spaces/YOUR_USERNAME/closed-book-qa

# Check space logs
# Available in HF Spaces web interface
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/closed-book-qa
cd closed-book-qa

# Make your changes
# ...

# Push updates
git add .
git commit -m "Update application"
git push
```

### Environment Variable Updates
1. Go to your HF Space settings
2. Update environment variables
3. Redeploy the space

## 💰 Cost Optimization

### HF Spaces Cost Optimization
- **Free Tier**: 16GB RAM, CPU only
- **Paid Tier**: 32GB RAM, GPU available
- **Auto-scaling**: Automatic based on usage
- **Pay-per-use**: Only pay for what you use

### Performance Tips
- Use appropriate memory allocation
- Optimize vector store loading
- Implement proper caching
- Monitor resource usage

## 🔐 Security

### Best Practices
1. Store API keys in environment variables
2. Use HTTPS for all communications
3. Implement proper error handling
4. Monitor access logs
5. Regular security updates

### API Key Management
```bash
# Set environment variable in HF Spaces
GOOGLE_API_KEY=your_google_api_key_here

# Never commit API keys to git
echo "*.env" >> .gitignore
```

## 📊 Performance Optimization

### Streamlit Optimizations
- Use session state for caching
- Implement proper error handling
- Optimize UI components
- Use async operations where possible

### RAG Pipeline Optimizations
- Cache vector stores in memory
- Use efficient embedding models
- Implement proper chunking strategies
- Optimize retrieval algorithms

## 🆘 Support

For issues and support:
- Check HF Spaces logs
- Review application logs
- Test endpoints individually
- Verify environment variables
- Check resource allocation

## 📝 Notes

- The Streamlit frontend is optimized for HF Spaces deployment
- Vector stores are pre-loaded on startup for better performance
- Async operations are used throughout for better scalability
- Health checks are implemented for monitoring
- Error handling is comprehensive for production use

## 🎯 Advantages of HF Spaces

| Feature | HF Spaces | Streamlit Cloud | GCP |
|---------|-----------|-----------------|-----|
| **Free Tier** | ✅ Generous | ✅ Limited | ❌ Pay-per-use |
| **GPU Support** | ✅ Available | ❌ No | ✅ Available |
| **Deployment** | ✅ Very Easy | ✅ Easy | ⚠️ Complex |
| **Community** | ✅ Active | ⚠️ Limited | ❌ None |
| **Monitoring** | ✅ Built-in | ⚠️ Basic | ✅ Advanced |
| **Scaling** | ✅ Auto | ⚠️ Limited | ✅ Advanced |

## 🚀 Next Steps

1. **Deploy to HF Spaces** using the provided scripts
2. **Test the application** thoroughly
3. **Monitor performance** and optimize as needed
4. **Share your space** with the community
5. **Gather feedback** and iterate

HF Spaces is an excellent choice for your RAG application, offering a great balance of ease of use, performance, and community features! 