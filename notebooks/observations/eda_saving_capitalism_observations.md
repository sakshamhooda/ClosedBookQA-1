# EDA Observations for "Saving Capitalism from the Capitalists"

This document summarizes the comprehensive findings from the Exploratory Data Analysis (EDA) of "Saving Capitalism from the Capitalists" by Raghuram Rajan and Luigi Zingales (2003).

## 1. File Information and Basic Statistics

### File Details
- **EPUB Size:** 0.73 MB
- **PDF Size:** 2.82 MB
- **Format:** EPUB/PDF Analysis

### Text Statistics
- **Total Words:** 157,789
- **Total Sentences:** 6,960
- **Unique Words:** 11,881
- **Unique Words (no stopwords):** 9,351
- **Average Sentence Length:** 22.7 words
- **Vocabulary Size:** 11,881

### Additional Statistics
- **Average sentence length:** 19.8 words
- **Median sentence length:** 17.0 words
- **Sentence length std dev:** 15.0 words
- **Longest sentence:** 126 words
- **Shortest sentence:** 1 words

The book has a moderate average sentence length, suggesting a balanced academic writing style. The vocabulary is substantial, which is typical for a book on economics and finance.

## 2. Word and Bigram Frequencies

### Most Common Words (with stopwords)
1. the - 9,632
2. , - 9,231
3. . - 6,217
4. of - 4,986
5. to - 4,400
6. and - 3,303
7. in - 3,269
8. a - 2,473
9. that - 1,592
10. is - 1,441

### Most Common Words (excluding stopwords)
1. financial - 626
2. text - 487
3. market - 449
4. markets - 439
5. firms - 409
6. finance - 393
7. government - 389
8. new - 367
9. economic - 359
10. would - 339

### Most Common Bigrams
1. of the - 1,174
2. in the - 999
3. to text - 486
4. to the - 351
5. and the - 343
6. for the - 227
7. that the - 227
8. it is - 220
9. on the - 216
10. to be - 202

The most frequent words and bigrams are highly relevant to the book's central themes of finance, markets, government, and economics. This confirms that the text extraction process was successful in capturing the core content of the book.

## 3. Structural Analysis

### EPUB Structure Issues
- **EPUB Analysis Error:** The EPUB structure analysis encountered an error due to spine item format issues
- **Spine Items:** Could not be fully analyzed due to format inconsistencies
- **TOC Entries:** Could not be extracted due to structure issues

### Chapter Analysis
- **Total Chapters:** 30 chapters identified
- **Average words per chapter:** 5,291
- **Longest chapter:** 12,700 words (Notes section)
- **Shortest chapter:** 3 words

### Chapter-level Chunk Analysis
- **toc:** 136 words → 1 chunks
- **ded:** 3 words → 1 chunks
- **prf:** 1,084 words → 7 chunks
- **itr:** 8,030 words → 51 chunks
- **p01:** 6 words → 1 chunks
- **c01:** 7,389 words → 47 chunks
- **c02:** 9,253 words → 59 chunks
- **c03:** 9,754 words → 62 chunks
- **c04:** 6,030 words → 39 chunks
- **c05:** 6,920 words → 44 chunks
- **p02:** 7 words → 1 chunks
- **c06:** 11,321 words → 72 chunks
- **c07:** 5,805 words → 37 chunks
- **c08:** 9,786 words → 63 chunks
- **p03:** 6 words → 1 chunks
- **c09:** 9,182 words → 59 chunks
- **c10:** 8,128 words → 52 chunks
- **c11:** 9,754 words → 62 chunks
- **p04:** 10 words → 1 chunks
- **c12:** 7,207 words → 46 chunks
- **c13:** 6,995 words → 45 chunks
- **con:** 1,201 words → 8 chunks
- **nts:** 12,700 words → 81 chunks (Notes section)
- **bib:** 6,473 words → 42 chunks (Bibliography)
- **ata:** 247 words → 2 chunks
- **cop:** 143 words → 1 chunks

## 4. Chunking Strategy Analysis

### RAG Implementation Parameters
- **Total estimated tokens:** 205,125
- **Chunk size:** 220 tokens
- **Overlap:** 15 tokens
- **Effective chunk size:** 205 tokens
- **Total number of chunks:** 1,001
- **Average chunks per chapter:** 34.0

### Gemini Flash 2.5 Context Analysis
- **Context window:** 8,000 tokens
- **Max chunks per query:** ~34
- **Chunks that fit:** 34

The chunking strategy is optimized for Gemini Flash 2.5's context window, ensuring efficient processing while maintaining content coherence.

## 5. Special Content Analysis

### Content Types Found
- **Footnotes found:** 485
- **Images found:** 5
- **Tables found:** 0
- **End-notes sections:** 9

### Image Analysis
The book contains 5 images:
- images/Raja_9781400049165_epub_cvi_r1.jpg
- images/Raja_9781400049165_epub_004_r1.jpg
- images/Raja_9781400049165_epub_001_r1.jpg
- images/Raja_9781400049165_epub_002_r1.jpg
- images/Raja_9781400049165_epub_003_r1.jpg

### Footnote Analysis
- **Unique footnote references:** 59
- **Footnote numbers range:** 1 - 9
- **Total footnote instances:** 485

The book contains dense footnotes that require special handling during the RAG implementation.

## 6. RAG Implementation Recommendations

### Chunking Strategy
- **Chunk size:** 220 tokens
- **Overlap:** 15 tokens
- **Estimated chunks:** 1,001
- **Reasoning:** Optimized for Gemini Flash 2.5 context window (8k tokens)

### Footnote Handling
- **Strip anchors:** True
- **Separate chunks:** True
- **Reasoning:** Keep end-notes as separate chunks for specific queries like "what does note 42 say?"

### Image Handling
- **Strip images:** True
- **Add placeholders:** True
- **Reasoning:** Limited images (5 JPGs) - add metadata placeholders for future vision encoder

### Metadata Structure
- **Fields:** ['chunk_text', 'embedding', 'chunk_id', 'chapter', 'part', 'pdf_page', 'has_image']
- **Reasoning:** Comprehensive metadata for accurate citations and filtering

### Index Strategy
- **Index name:** index_capitalism
- **Isolation:** Separate from debt crisis index
- **Reasoning:** Ensure no cross-contamination between books

### Retrieval Strategy
- **Hybrid search:** True
- **BM25 reranking:** True
- **Cross-encoder:** bge-reranker-base
- **Final chunks:** 3
- **Reasoning:** Hybrid approach for better relevance

### Prompt Template
- **Format:** JSON structured
- **Template:** { "task": "qa", "ground_truth_passages": [...], "question": "..." }
- **Reasoning:** Gemini prefers structured JSON prompts

### Grounding Strategy
- **Self-check:** True
- **Verify call:** True
- **Reasoning:** Use Gemini Flash for cheap verification calls

## 7. Summary for RAG Implementation

### Key Statistics
- **Estimated chunks:** 1,001
- **Footnotes to handle:** 485
- **Images to placeholder:** 5
- **Tables to preserve:** 0
- **End-notes sections:** 9

### Implementation Priorities
1. **Fix EPUB structure parsing** to extract proper spine and TOC information
2. **Implement footnote handling** with anchor stripping and separate chunking
3. **Add image placeholders** for future vision encoder integration
4. **Create isolated index** to prevent cross-contamination with Big Debt Crisis
5. **Implement hybrid retrieval** with BM25 and cross-encoder reranking
6. **Use JSON prompt templates** optimized for Gemini Flash 2.5

### Technical Considerations
- The book has a substantial amount of content (157,789 words) requiring efficient chunking
- Footnotes are dense and need special processing
- Images are minimal but should be handled with placeholders
- The Notes section (12,700 words) is the longest and most complex
- Chapter boundaries should be respected during chunking

This analysis provides a comprehensive foundation for implementing the RAG-based question-answering system for "Saving Capitalism from the Capitalists" as outlined in the development plan.
