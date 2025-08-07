import os
import json
from typing import List, Dict, Any

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = "models/embedding-001"
RERANK_MODEL = "bge-reranker-base"  # Placeholder – would need actual implementation
MAX_FINAL_PASSAGES = 5

# -----------------------------------------------------------------------------
# Vector store utilities
# -----------------------------------------------------------------------------


def _vs_path(book_id: str) -> str:
    return os.path.join(
        "vector_store",
        "big_debt_crisis" if book_id == "debt_crisis" else "saving_capitalism",
    )


def load_vector_store(book_id: str) -> FAISS:
    embeddings: Embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
    return FAISS.load_local(
        _vs_path(book_id), embeddings, allow_dangerous_deserialization=True
    )


# -----------------------------------------------------------------------------
# Retrieval Pipeline
# -----------------------------------------------------------------------------


def _bm25_retriever(docs: List[Document]):
    """Instantiate a BM25 retriever from existing docs (placeholder)."""
    return BM25Retriever.from_documents(docs)


def _rerank(question: str, docs: List[Document]) -> List[Document]:
    """Placeholder reranker that returns docs unchanged.
    Integrate bge-reranker-base later.
    """
    return docs


def retrieve(question: str, book_id: str) -> List[Document]:
    """Hybrid retrieval: BM25 + FAISS + rerank, returns top passages."""
    vs = load_vector_store(book_id)

    # Vector similarity
    vec_docs = vs.similarity_search(question, k=10)

    # Build lightweight BM25 over raw texts retrieved
    bm25 = _bm25_retriever(vec_docs)
    bm25_docs = bm25.get_relevant_documents(question)

    # Merge and dedupe by page_content
    merged: Dict[str, Document] = {d.page_content: d for d in vec_docs + bm25_docs}

    reranked = _rerank(question, list(merged.values()))

    return reranked[:MAX_FINAL_PASSAGES]


# -----------------------------------------------------------------------------
# Generation & Verification (Gemini)
# -----------------------------------------------------------------------------

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def _prompt_json(question: str, passages: List[Document]) -> str:
    content = {
        "task": "qa",
        "ground_truth_passages": [p.page_content for p in passages],
        "question": question,
    }
    return json.dumps(content, ensure_ascii=False)


def generate_answer(question: str, passages: List[Document]) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = _prompt_json(question, passages)
    resp = model.generate_content(prompt)
    return resp.text


def verify_answer(answer: str, passages: List[Document]) -> bool:
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = json.dumps(
        {
            "task": "verify",
            "answer": answer,
            "ground_truth_passages": [p.page_content for p in passages],
        }
    )
    resp = model.generate_content(prompt)
    return "yes" in resp.text.lower()

