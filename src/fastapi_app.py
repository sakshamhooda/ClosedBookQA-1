from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import time
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys
from functools import lru_cache

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import retrieve, generate_answer
from src.eda_api import compute_eda_summary
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Closed Book QA API",
    description="RAG-based Question Answering API for financial books",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    book_id: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    status: str = "success"

class HealthResponse(BaseModel):
    status: str
    vector_stores_loaded: List[str]
    embeddings_model_loaded: bool

# Global cache for expensive resources
vector_stores = {}
embeddings_model = None

# Cache the embedding model
@lru_cache(maxsize=1)
def get_embeddings():
    """Get cached embeddings model."""
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def get_vector_store(book_id: str) -> FAISS:
    """Get cached vector store for a book."""
    if book_id not in vector_stores:
        embeddings = get_embeddings()
        vs_path = os.path.join(
            "vector_store",
            "big_debt_crisis" if book_id == "debt_crisis" else "saving_capitalism",
        )
        vector_stores[book_id] = FAISS.load_local(
            vs_path, embeddings, allow_dangerous_deserialization=True
        )
    return vector_stores[book_id]

@app.on_event("startup")
async def startup_event():
    """Initialize expensive resources on startup."""
    global embeddings_model, vector_stores
    
    try:
        # Initialize embeddings model once
        embeddings_model = get_embeddings()
        print("✅ Embeddings model loaded successfully")
        
        # Pre-load vector stores
        book_ids = ["debt_crisis", "capitalism"]
        for book_id in book_ids:
            try:
                get_vector_store(book_id)
                print(f"✅ Vector store loaded for {book_id}")
            except Exception as e:
                print(f"❌ Failed to load vector store for {book_id}: {e}")
                
    except Exception as e:
        print(f"❌ Startup error: {e}")

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Async endpoint for asking questions."""
    start_time = time.time()
    
    try:
        # Validate book_id
        if request.book_id not in ["debt_crisis", "capitalism"]:
            raise HTTPException(status_code=400, detail="Invalid book_id")
        
        # Check if vector store is loaded
        if request.book_id not in vector_stores:
            raise HTTPException(
                status_code=503, 
                detail=f"Vector store for {request.book_id} not loaded"
            )
        
        # Retrieve passages (async)
        passages = await asyncio.to_thread(
            retrieve, request.question, request.book_id
        )
        
        # Generate answer (async)
        answer = await asyncio.to_thread(
            generate_answer, request.question, passages
        )
        
        # Format sources
        sources = []
        for i, doc in enumerate(passages):
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "rank": i + 1
            })
        
        processing_time = time.time() - start_time
        
        return QuestionResponse(
            answer=answer,
            sources=sources,
            processing_time=processing_time,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return QuestionResponse(
            answer=f"Error processing request: {str(e)}",
            sources=[],
            processing_time=processing_time,
            status="error"
        )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        vector_stores_loaded=list(vector_stores.keys()),
        embeddings_model_loaded=embeddings_model is not None
    )

@app.get("/api/books")
async def get_available_books():
    """Get available books."""
    return {
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


@app.get("/api/eda/summary")
async def eda_summary(
    book_id: str = Query(..., pattern="^(debt_crisis|capitalism)$"),
    include_wordcloud: bool = Query(True),
):
    """Return a computed EDA summary for the requested book.

    This endpoint offloads EDA computation to the backend to avoid heavy
    operations in the Streamlit frontend on Cloud Run.
    """
    try:
        summary = compute_eda_summary(book_id, include_wordcloud)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EDA computation failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "status": "error"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000))) 