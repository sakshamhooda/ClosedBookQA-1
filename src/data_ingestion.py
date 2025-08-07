import os
import uuid
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from tqdm import tqdm
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .utils import estimate_pdf_page, find_image_refs, _approx_token_len

load_dotenv()
CHUNK_SIZE_TOKENS = 220
CHUNK_OVERLAP_TOKENS = 15
EMBED_MODEL = "models/embedding-001"

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def clean_text(html: str, book_id: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img"):
        img.decompose()
    if book_id == "capitalism":
        for sup in soup.find_all("sup"):
            sup.decompose()
    return soup.get_text(separator=" ", strip=True)


def _chunk_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",  # A reasonable proxy for Gemini's tokenizer
        chunk_size=CHUNK_SIZE_TOKENS,
        chunk_overlap=CHUNK_OVERLAP_TOKENS,
    )
    chunked_docs = []
    for doc in tqdm(docs, desc="Chunking documents"):
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            new_doc = doc.copy()
            new_doc["text"] = chunk
            chunked_docs.append(new_doc)
    return chunked_docs


def ingest_book(book_id: str, epub_path: str, pdf_path: str = None) -> None:
    if book_id not in {"debt_crisis", "capitalism"}:
        raise ValueError("book_id must be 'debt_crisis' or 'capitalism'")

    print(f"Ingesting {book_id} from {epub_path} ...")
    book = epub.read_epub(epub_path)

    # ------------------------------------------------------------------
    # 1. Extract content and initial metadata from EPUB items
    # ------------------------------------------------------------------
    docs_to_chunk = []
    token_offset = 0

    for item in tqdm(book.get_items(), desc="Parsing EPUB items"):
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        
        html = item.get_content()
        text = clean_text(html, book_id)
        if not text.strip():
            continue

        image_refs = find_image_refs(html.decode("utf-8", "ignore"))
        
        # Estimate PDF page based on token offset
        page_estimate = estimate_pdf_page(token_offset)

        docs_to_chunk.append({
            "text": text,
            "metadata": {
                "chapter": item.get_name(),
                "part": None, # Could be improved by parsing TOC
                "pdf_page": page_estimate,
                "has_image": len(image_refs) > 0,
                "image_refs": image_refs,
                "book_id": book_id,
            }
        })
        token_offset += _approx_token_len(text)

    # ------------------------------------------------------------------
    # 2. Chunk documents
    # ------------------------------------------------------------------
    chunked_docs = _chunk_docs(docs_to_chunk)
    texts = [doc["text"] for doc in chunked_docs]
    metadatas = [doc["metadata"] for doc in chunked_docs]
    
    # Add unique chunk ID to each metadata object
    for meta in metadatas:
        meta["chunk_id"] = str(uuid.uuid4())
        
    print(f"Total chunks created: {len(texts)}")

    # ------------------------------------------------------------------
    # 3. Embeddings & Vector store
    # ------------------------------------------------------------------
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
    vs = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)

    # ------------------------------------------------------------------
    # 4. Persist
    # ------------------------------------------------------------------
    out_dir_map = {"debt_crisis": "big_debt_crisis", "capitalism": "saving_capitalism"}
    out_dir = os.path.join("vector_store", out_dir_map[book_id])
    os.makedirs(out_dir, exist_ok=True)
    vs.save_local(out_dir)

    meta_json_path = os.path.join(out_dir, "metadata.json")
    with open(meta_json_path, "w", encoding="utf-8") as fp:
        json.dump(metadatas, fp, ensure_ascii=False, indent=2)

    print(f"Finished ingesting {book_id}. Index stored at {out_dir}")

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ingest_book(
        "debt_crisis",
        "data/BigDebtCrisis_RayDalio.epub",
        "data/BigDebtCrisis_RayDalio.pdf",
    )
    ingest_book(
        "capitalism",
        "data/SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub",
        "data/SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.pdf",
    )

