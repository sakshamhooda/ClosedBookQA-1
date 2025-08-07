import re
from typing import Optional, Tuple, List

# -----------------------------------------------------------------------------
# Tokenizer utilities (crude)
# -----------------------------------------------------------------------------

def _approx_token_len(text: str) -> int:
    """Very rough token heuristic: ~4 chars per token."""
    return int(len(text) / 4)

# -----------------------------------------------------------------------------
# PDF Page Mapping (stub)
# -----------------------------------------------------------------------------

def estimate_pdf_page(token_offset: int, tokens_per_page: int = 450) -> int:
    """Rudimentary mapping from token offset to PDF page number.

    Args:
        token_offset: Index of first token in the chunk within the whole book.
        tokens_per_page: Empirical average tokens per page.
    Returns:
        1-based page number estimate.
    """
    return max(1, int(token_offset / tokens_per_page) + 1)

# -----------------------------------------------------------------------------
# Image reference extraction
# -----------------------------------------------------------------------------

def find_image_refs(html: str) -> List[str]:
    """Return list of image filenames referenced in the HTML snippet."""
    # This regex is basic and might need to be made more robust
    return re.findall(r'src="[^"]+\/([^"]+\.(?:png|jpg|jpeg|gif))"', html, re.I)

