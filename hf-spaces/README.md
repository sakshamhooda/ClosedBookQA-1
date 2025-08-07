---
title: Closed Book QA
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.1
app_file: app.py
pinned: false
license: mit
---

# Closed Book QA

A RAG-based Question Answering system for financial books using Streamlit and Gemini.

## Features

- 📖 Query two financial books: "Big Debt Crisis" and "Saving Capitalism"
- 🔍 Advanced RAG pipeline with hybrid retrieval
- ⚡ Fast response times with async processing
- 📊 Source citations with metadata
- 🎯 Accurate answers grounded in book content

## Usage

1. Select a book from the dropdown
2. Ask your question in the text area
3. Get instant answers with source citations
4. View processing time and metadata

## Technology Stack

- **Backend**: FastAPI with async operations
- **RAG**: Gemini embeddings + FAISS vector store
- **LLM**: Gemini 2.5 Flash for generation
- **Frontend**: Streamlit for easy interaction
- **Deployment**: Hugging Face Spaces

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/ask` - Ask questions
- `GET /api/books` - List available books 