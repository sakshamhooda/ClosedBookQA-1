# EDA Observations for "Big Debt Crisis"

This document summarizes the key findings from the Exploratory Data Analysis (EDA) of "Big Debt Crisis" by Ray Dalio.

## 1. Basic Textual Analysis

- **Total Words**: 214,469
- **Total Sentences**: 7,214
- **Unique Words**: 11,692
- **Unique Words (no stopwords)**: 8,279
- **Average Sentence Length**: 29.7 words
- **Vocabulary Size**: 11,692

**File Information:**
- **EPUB Size**: 23.14 MB
- **PDF Size**: 30.30 MB

Compared to the previous analysis, this book has a significantly larger word count and longer average sentence length, suggesting a more comprehensive and detailed treatment of the subject matter.

## 2. Word and Bigram Frequencies

### Most Common Words (excluding stopwords):
1. **debt** - 942 occurrences
2. **york** - 758 occurrences
3. **times** - 746 occurrences
4. **currency** - 732 occurrences
5. **money** - 601 occurrences
6. **policy** - 596 occurrences
7. **financial** - 576 occurrences
8. **percent** - 562 occurrences
9. **gdp** - 557 occurrences
10. **credit** - 544 occurrences

### Most Common Bigrams:
1. **of the** - 1,238 occurrences
2. **in the** - 1,163 occurrences
3. **york times** - 672 occurrences
4. **to the** - 467 occurrences
5. **and the** - 419 occurrences
6. **of gdp** - 344 occurrences
7. **policy makers** - 308 occurrences
8. **the bubble** - 291 occurrences
9. **that the** - 279 occurrences
10. **on the** - 273 occurrences

The most frequent words and bigrams are centered around the themes of debt, financial crises, monetary policy, and economic indicators. The high frequency of "york times" suggests significant reference to news sources and historical events.

## 3. Structural Analysis

### Chapter Statistics:
- **Average words per chapter**: 18,610
- **Longest chapter**: 31,848 words
- **Shortest chapter**: 10 words

The book contains 9 main sections with varying content density, indicating a structured approach to presenting different aspects of debt crises.

## 4. Chunking Strategy Analysis

### RAG Implementation Parameters:
- **Total estimated tokens**: 278,809
- **Chunk size**: 220 tokens
- **Overlap**: 15 tokens
- **Effective chunk size**: 205 tokens
- **Total number of chunks**: 1,361
- **Average chunks per chapter**: 118.4

### Chapter-level Chunk Distribution:
- **id_1**: 30,757 words → 196 chunks
- **id_2**: 21,729 words → 138 chunks
- **id_3**: 17,456 words → 111 chunks
- **id_4**: 21,528 words → 137 chunks
- **id_5**: 31,848 words → 202 chunks
- **id_6**: 23,953 words → 152 chunks
- **id_7**: 18,392 words → 117 chunks
- **id_8**: 16,494 words → 105 chunks
- **chapter_0**: 10 words → 1 chunk
- **id_9**: 3,930 words → 25 chunks

### Gemini Flash 2.5 Context Analysis:
- **Context window**: 8,000 tokens
- **Max chunks per query**: ~34
- **Chunks that fit**: 34

## 5. Special Content Analysis

### Visual and Structural Elements:
- **Images found**: 1,608
- **Footnotes found**: 0
- **Tables found**: 0
- **End-notes sections**: 5

### Image Analysis:
The book contains a significant number of images (1,608), likely including charts, graphs, and visual data representations. Sample image files include:
- Image01458.jpg
- Image01460.jpg
- Image01462.jpg
- Image01465.jpg
- Image01467.jpg

## 6. RAG Implementation Recommendations

### Chunking Strategy:
- **Chunk size**: 220 tokens (optimized for Gemini Flash 2.5 context window)
- **Overlap**: 15 tokens for continuity
- **Reasoning**: Optimized for 8k token context window

### Content Handling:
- **Image handling**: Strip images and add metadata placeholders for future vision encoder integration
- **Footnote handling**: Strip anchors and keep end-notes as separate chunks for specific queries
- **Table handling**: Preserve table structure and include in chunk metadata

### Metadata Structure:
- **Fields**: chunk_text, embedding, chunk_id, chapter, part, pdf_page, has_image
- **Reasoning**: Comprehensive metadata for accurate citations and filtering

### Index Strategy:
- **Index name**: index_debt_crisis
- **Isolation**: Separate from capitalism index to prevent cross-contamination
- **Reasoning**: Ensure no cross-contamination between books

### Retrieval Strategy:
- **Hybrid search**: True
- **BM25 reranking**: True
- **Cross-encoder**: bge-reranker-base
- **Final chunks**: 3
- **Reasoning**: Hybrid approach for better relevance

### Prompt Template:
- **Format**: JSON structured
- **Template**: { "task": "qa", "ground_truth_passages": [...], "question": "..." }
- **Reasoning**: Gemini prefers structured JSON prompts

### Grounding Strategy:
- **Self-check**: True
- **Verify call**: True
- **Reasoning**: Use Gemini Flash for cheap verification calls

## 7. Implications for RAG Pipeline

### Key Considerations:
1. **High Image Content**: With 1,608 images, the book requires careful handling of visual elements during chunking
2. **Large Vocabulary**: 11,692 unique words indicate rich, technical content requiring sophisticated embedding
3. **Structured Content**: 5 end-notes sections suggest organized reference material
4. **Optimal Chunking**: 1,361 chunks provide good granularity for retrieval
5. **Context Optimization**: 34 chunks fit within Gemini's context window, enabling comprehensive answers

### Performance Optimizations:
- Use chapter-level filtering for targeted queries
- Implement image placeholder metadata for future vision integration
- Maintain end-notes as separate chunks for reference queries
- Leverage hybrid search for better relevance
- Use structured JSON prompts for Gemini compatibility
