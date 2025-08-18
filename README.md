# ClosedBookQA-1

End‑to‑end, closed‑book RAG Question Answering app over two economics books:

- "Big Debt Crisis" by Ray Dalio
- "Saving Capitalism from the Capitalists" by Raghuram Rajan & Luigi Zingales

The system builds isolated FAISS indexes per book, retrieves grounded passages, and uses Google Gemini to generate and verify answers. A Streamlit UI lets users query a selected book and view sources with chapter and approximate PDF page references.

> [!WARNING]
> **UPDATE | 19.08.2025:** I've stalled deployment from GCP due to cost reasons.  
> Demo shall not be accessible through the stated link anymore.  
> Please follow the instructions related to the Dockerfile to deploy your image instance.


## Table of Contents

- Overview
- Features
- Architecture
- Project Structure
- Setup and Installation
- Configuration (.env)
- Data Ingestion and Indexing
- Running the App
- Usage Guide
- Observations and Findings (Non‑technical summaries)
- Troubleshooting
- Roadmap
- License and Credits


## Overview

ClosedBookQA-1 is a focused RAG application that answers questions strictly from the contents of the selected book. It maintains two independent pipelines and vector stores to avoid cross‑contamination across books.


## Features

- Isolated FAISS indexes for each book
- Hybrid retrieval (FAISS similarity + lightweight BM25 over retrieved texts)
- Gemini‑based answer generation with structured JSON prompts
- Optional answer verification (self‑check) via Gemini
- Streamlit chat UI with per‑answer source citations
- In‑app re‑ingestion button to rebuild both indexes


## Architecture

High‑level flow:

1) Ingestion (EPUB → clean → chunk → embed) → FAISS per book
2) Retrieval (FAISS top‑k → BM25 over retrieved → merge/dedupe → rerank placeholder) → top passages
3) Generation (Gemini 2.5 Flash) using a JSON‑structured prompt grounded on retrieved passages
4) Optional verification (Gemini) to self‑check if the answer is supported by the passages

Key modules:

- `src/data_ingestion.py`: EPUB parsing, cleaning, chunking, embeddings, FAISS persistence
- `src/rag.py`: FAISS loading, hybrid retrieval, Gemini generation and verification
- `src/app.py`: Streamlit application (chat interface, book selector, re‑ingestion)
- `src/utils.py`: Token length heuristic, PDF page estimation, image reference extraction

Current models and parameters:

- Embeddings: `models/embedding-001` (Google Generative AI)
- Generator: `gemini-2.5-flash`
- Retrieval: FAISS top‑k (10) + BM25 over that set, final cap at 5 passages
- Chunking: 220 tokens, 15 token overlap (approx tokenizer proxy)

Limitations (intentional for v1):

- Reranker is a placeholder (listed as `bge-reranker-base` to be integrated)
- PDF page mapping is estimated from token offsets
- Images are stripped at ingestion; image refs kept in metadata
- Footnotes are stripped (capitalism) and end‑notes not handled specially yet


## Project Structure

```
ClosedBookQA-1/
  data/                               # local EPUB/PDF files (not tracked)
  notebooks/observations/             # EDA summaries for each book
  src/
    app.py                            # Streamlit UI
    data_ingestion.py                 # Ingestion → FAISS per book
    rag.py                            # Retrieval + Generation + Verify
    utils.py                          # Helpers (tokens, pdf page, image refs)
  vector_store/
    big_debt_crisis/                  # FAISS + metadata for Dalio book
    saving_capitalism/                # FAISS + metadata for Rajan/Zingales
  requirements.txt
  README.md
```


## Setup and Installation

Prereqs:

- Python 3.10+
- macOS/Linux/Windows
- Google API key with Generative AI access

Create and activate a virtual environment (recommended `.venv`):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```


## Configuration (.env)

Create a `.env` file in the project root with at least:

```bash
GOOGLE_API_KEY=your_api_key_here
```

The app reads environment variables via `python-dotenv`.


## Data Ingestion and Indexing

There are two ingestion paths:

1) From the Streamlit sidebar, click "Re‑ingest Both Books". This will parse the EPUBs, clean and chunk text, embed with Gemini embeddings, then persist FAISS indexes and metadata under `vector_store/`.
2) Run the ingestion script directly:

```bash
source .venv/bin/activate
python -m src.data_ingestion
```

Inputs and outputs:

- Inputs: EPUB files in `data/`
  - `data/BigDebtCrisis_RayDalio.epub`
  - `data/SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub`
- Outputs per book:
  - FAISS: `vector_store/<book_dir>/index.faiss`, `index.pkl`
  - Metadata: `vector_store/<book_dir>/metadata.json`

Notes:

- Existing indexes are already provided under `vector_store/` to start querying immediately.
- The ingestion also writes a UUID `chunk_id` into each chunk’s metadata, and estimates `pdf_page` from token offsets.


## Running the App

### Local Development

```bash
source .venv/bin/activate
streamlit run src/app.py
```

Then open the local URL printed by Streamlit (usually `http://localhost:8501`).

## Deployment

### GCP Cloud Run Deployment (Recommended)

The application is designed for deployment on Google Cloud Platform using Cloud Run. The deployment includes both FastAPI backend and Streamlit frontend in a single container for optimal performance and cost efficiency.

#### Architecture

```
┌─────────────────────────────────────┐
│         Single Container            │
│  ┌─────────────┐ ┌─────────────┐   │
│  │   FastAPI   │ │  Streamlit  │   │
│  │   Port 8000 │ │  Port 8080  │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Benefits:**
- ✅ Single deployment - easier to manage
- ✅ No CORS issues - same domain
- ✅ Cost effective - one service instead of two
- ✅ Faster package installation - using `uv`
- ✅ Simplified architecture - everything in one place

#### Prerequisites

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

#### Automated Deployment

```bash
# Deploy to GCP Cloud Run
./deploy-gcp.sh
```

This script will:
- Build the container with both FastAPI and Streamlit
- Deploy to Cloud Run with optimized settings
- Set up environment variables
- Provide the deployment URL

#### Manual Deployment

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/closedbook-qa-saksham
gcloud run deploy closedbook-qa-saksham \
    --image gcr.io/$PROJECT_ID/closedbook-qa-saksham \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY"
```

#### Deployment Configuration

| Service | CPU | Memory | Timeout | Concurrency |
|---------|-----|--------|---------|-------------|
| Cloud Run | 2 | 2Gi | 300s | 80 |

#### API Endpoints

After deployment, your service will be available at:
- **Frontend**: `https://your-service-url` (Streamlit UI)
- **API Health**: `https://your-service-url/api/health`
- **Ask Question**: `https://your-service-url/api/ask`
- **Available Books**: `https://your-service-url/api/books`

#### Testing the Deployment

```bash
# Health check
curl https://your-service-url/api/health

# Test asking a question
curl -X POST "https://your-service-url/api/ask" \
     -H "Content-Type: application/json" \
     -d '{"question":"What is a debt crisis?","book_id":"debt_crisis"}'
```

#### Monitoring

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=closedbook-qa-saksham"

# View metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

#### Troubleshooting Deployment

1. **Container Startup Issues**:
   - Check logs: `gcloud run services logs read closedbook-qa-saksham`
   - Verify environment variables are set correctly
   - Ensure API key has proper permissions

2. **Memory Issues**:
   - Increase memory allocation in deployment configuration
   - Monitor resource usage in Cloud Console

3. **Timeout Issues**:
   - Increase timeout in deployment configuration
   - Optimize RAG pipeline performance

For detailed GCP deployment documentation, see [README-GCP.md](README-GCP.md).


## Usage Guide

1) Choose a book in the sidebar.
2) Type a question in the chat input. The app will:
   - Retrieve top passages (hybrid FAISS + BM25) from the selected book
   - Generate an answer using Gemini 2.5 Flash grounded strictly on those passages
   - Show the answer and list the sources (chapter, approx PDF page, book id)
3) Optionally, use "Re‑ingest Both Books" to rebuild indexes if you change ingestion settings or data files.


## Observations and Findings (Non‑technical summaries)

Summaries from the EDA notebooks under `notebooks/observations/`.

### Big Debt Crisis (Ray Dalio)

- Scale: ~214k words across 9 main sections; average sentence ~29.7 words
- Dominant themes: debt, financial crises, monetary policy, GDP and credit metrics
- Rich visuals: ~1,600 images, suggesting heavy use of charts/figures
- Chunking plan: 220‑token chunks with 15 overlap → ~1,361 chunks
- Retrieval guidance: hybrid search, BM25 reranking, cross‑encoder (future)
- Prompting: JSON structured prompts for Gemini; enable self‑check

See full details: `notebooks/observations/eda_big_debt_crises_observations.md`.

### Saving Capitalism from the Capitalists (Rajan & Zingales)

- Scale: ~158k words across ~30 chapters; moderate academic style
- Dense footnotes: 485 instances; limited images (5)
- Chunking plan: 220‑token chunks with 15 overlap → ~1,001 chunks
- Retrieval guidance: hybrid search, BM25 reranking, cross‑encoder (future)
- Prompting: JSON structured prompts for Gemini; enable self‑check

See full details: `notebooks/observations/eda_saving_capitalism_observations.md`.


## Troubleshooting

- Missing Google API key: Ensure `.env` contains `GOOGLE_API_KEY` and the shell has access to it.
- FAISS load error: Ensure indexes exist under `vector_store/<book>/`. Re‑ingest via the app or `python -m src.data_ingestion`.
- EPUB parsing issues: Requires `ebooklib` and `lxml`; re‑install dependencies if extraction fails.
- Mismatched environments: Activate `.venv` before running any command.
- Approximate PDF pages: Page numbers are estimated; they won’t match exact PDFs in all cases.


## Roadmap

- Integrate cross‑encoder reranker (e.g., `bge-reranker-base`)
- Improve PDF page alignment (TOC‑aware mapping, PDF text anchoring)
- Footnote/end‑note handling as dedicated chunks
- Light vision support via image placeholders
- Add unit tests and CI checks
- Add eval harness for answer quality and grounding fidelity


## License and Credits

- Code: MIT License (see `LICENSE`)
- Content: Books are copyrighted; local use only.
- Built by Saksham Hooda. Streamlit footer includes contact links.

