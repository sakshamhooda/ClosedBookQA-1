import base64
import io
import os
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple, Any

from bs4 import BeautifulSoup
from ebooklib import epub
from wordcloud import WordCloud
import numpy as np


STOPWORDS = {
    "the", "and", "a", "an", "to", "of", "in", "for", "on", "at", "by", "with",
    "is", "it", "this", "that", "as", "are", "be", "from", "or", "was", "were",
    "but", "not", "have", "has", "had", "you", "your", "we", "they", "their",
}


def _book_to_epub_path(book_id: str) -> Path:
    data_dir = Path("data")
    if book_id == "debt_crisis":
        return data_dir / "BigDebtCrisis_RayDalio.epub"
    elif book_id == "capitalism":
        return data_dir / "SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub"
    else:
        raise ValueError("Unsupported book_id. Use 'debt_crisis' or 'capitalism'.")


def _simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def _extract_texts(epub_path: Path) -> Tuple[str, List[Dict[str, Any]]]:
    book = epub.read_epub(str(epub_path))
    all_text: str = ""
    chapter_info: List[Dict[str, Any]] = []

    for item in book.get_items():
        if item.get_type() == 9:  # ebooklib.ITEM_DOCUMENT
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=" ")
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                all_text += text + " "
                chapter_info.append({
                    "id": item.get_id(),
                    "href": item.get_name(),
                    "text_length": len(text),
                    "word_count": len(_simple_tokenize(text)),
                })
    return all_text, chapter_info


def _split_sentences(all_text: str) -> List[str]:
    # Simple sentence splitter to avoid heavy NLTK dependency
    # Splits on ., !, ? followed by whitespace
    parts = re.split(r"(?<=[\.!\?])\s+", all_text)
    # Filter out very short fragments
    return [p.strip() for p in parts if len(p.strip()) > 0]


def _compute_stats(all_text: str, chapter_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    words = _simple_tokenize(all_text)
    words_no_stop = [w for w in words if w.isalpha() and w not in STOPWORDS]

    bigrams: List[str] = []
    for i in range(len(words_no_stop) - 1):
        bigrams.append(f"{words_no_stop[i]} {words_no_stop[i+1]}")

    word_freq = Counter(words)
    word_freq_no_stop = Counter(words_no_stop)
    bigram_freq = Counter(bigrams)

    top_words = word_freq.most_common(20)
    top_words_no_stop = word_freq_no_stop.most_common(20)
    top_bigrams = bigram_freq.most_common(15)

    # Sentence length distribution (approx)
    sentences = _split_sentences(all_text)
    sentence_lengths = [len(_simple_tokenize(s)) for s in sentences]
    # Histogram bins similar to notebook style (0-600 words)
    bin_edges = list(range(0, 601, 10))
    counts, edges = np.histogram(sentence_lengths, bins=bin_edges)

    return {
        "total_words": len(words),
        "unique_words": len(set(words)),
        "unique_words_no_stopwords": len(set(words_no_stop)),
        "top_words": top_words,
        "top_words_no_stopwords": top_words_no_stop,
        "top_bigrams": top_bigrams,
        "chapter_info": chapter_info,
        "words_no_stopwords": words_no_stop,  # used for wordcloud
        "sentence_length_hist": {
            "bin_edges": bin_edges,
            "counts": counts.tolist(),
        },
    }


def _generate_wordcloud_base64(words_no_stop: List[str]) -> str:
    if not words_no_stop:
        return ""
    wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words_no_stop))
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@lru_cache(maxsize=4)
def compute_eda_summary(book_id: str, include_wordcloud: bool = True) -> Dict[str, Any]:
    epub_path = _book_to_epub_path(book_id)
    all_text, chapter_info = _extract_texts(epub_path)
    stats = _compute_stats(all_text, chapter_info)

    response: Dict[str, Any] = {
        "book_id": book_id,
        "summary": {
            "total_words": stats["total_words"],
            "unique_words": stats["unique_words"],
            "unique_words_no_stopwords": stats["unique_words_no_stopwords"],
        },
        "chapter_info": stats["chapter_info"],
        "top_words": stats["top_words"],
        "top_words_no_stopwords": stats["top_words_no_stopwords"],
        "top_bigrams": stats["top_bigrams"],
        "sentence_length_hist": stats["sentence_length_hist"],
    }

    if include_wordcloud:
        response["wordcloud_png_base64"] = _generate_wordcloud_base64(stats["words_no_stopwords"])

    return response


