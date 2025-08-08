# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt stopwords

# Copy application code
COPY . .

# Create startup script for both services
RUN echo '#!/bin/bash \n\
# Start FastAPI in background on port 8000 \n\
uvicorn src.fastapi_app:app --host 0.0.0.0 --port 8000 & \n\
# Start Streamlit in foreground on port 8080 (main process) \n\
streamlit run src/streamlit_gcp_frontend.py --server.port 8080 --server.address 0.0.0.0' > /app/start.sh && chmod +x /app/start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the startup script
CMD ["/app/start.sh"] 