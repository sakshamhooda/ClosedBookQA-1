import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import warnings
import streamlit as st
from wordcloud import WordCloud

warnings.filterwarnings('ignore')

def eda_saving_capitalism():
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    # Set up plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    # File paths
    data_dir = Path("data")
    epub_file = data_dir / "SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub"

    # EPUB Structure Analysis
    def analyze_epub_structure(epub_path: Path) -> Dict[str, Any]:
        """Analyze the structure of an EPUB file."""
        try:
            book = epub.read_epub(epub_path)
            
            # Extract spine information
            spine_items = []
            for item in book.spine:
                spine_items.append({
                    'id': item[0],
                    'href': item[1].href if hasattr(item[1], 'href') else 'N/A',
                    'linear': item[1].linear if hasattr(item[1], 'linear') else 'N/A'
                })
            
            # Extract table of contents
            toc = []
            for item in book.toc:
                if hasattr(item, 'title'):
                    toc.append({
                        'title': item.title,
                        'href': item.href if hasattr(item, 'href') else None
                    })
            
            # Analyze document structure
            documents = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    documents.append({
                        'id': item.get_id(),
                        'href': item.get_name(),
                        'text_length': len(text),
                        'word_count': len(text.split()),
                        'has_images': len(soup.find_all('img')) > 0,
                        'has_tables': len(soup.find_all('table')) > 0,
                        'has_footnotes': len(soup.find_all(['sup', 'sub'])) > 0
                    })
            
            return {
                'spine_items': spine_items,
                'toc': toc,
                'documents': documents,
                'total_documents': len(documents),
                'total_words': sum(doc['word_count'] for doc in documents)
            }
        except Exception as e:
            return None

    epub_analysis = analyze_epub_structure(epub_file)

    # Content Extraction and Text Analysis
    def extract_text_content(epub_path: Path) -> Dict[str, Any]:
        """Extract and analyze text content from EPUB."""
        try:
            book = epub.read_epub(epub_path)
            
            all_text = ""
            chapter_texts = []
            chapter_info = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        all_text += text + " "
                        chapter_texts.append(text)
                        chapter_info.append({
                            'id': item.get_id(),
                            'href': item.get_name(),
                            'text_length': len(text),
                            'word_count': len(text.split())
                        })
            
            sentences = sent_tokenize(all_text)
            words = word_tokenize(all_text.lower())
            
            stop_words = set(stopwords.words('english'))
            words_no_stopwords = [word for word in words if word.isalpha() and word not in stop_words]
            
            bigrams = []
            for i in range(len(words) - 1):
                if words[i].isalpha() and words[i+1].isalpha():
                    bigrams.append(f"{words[i]} {words[i+1]}")
            
            return {
                'full_text': all_text,
                'chapter_texts': chapter_texts,
                'chapter_info': chapter_info,
                'sentences': sentences,
                'words': words,
                'words_no_stopwords': words_no_stopwords,
                'bigrams': bigrams,
                'total_sentences': len(sentences),
                'total_words': len(words),
                'unique_words': len(set(words)),
                'unique_words_no_stopwords': len(set(words_no_stopwords))
            }
        except Exception as e:
            return None

    text_analysis = extract_text_content(epub_file)

    # Frequency Analysis and Key Terms
    def analyze_frequencies(text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze word and bigram frequencies."""
        try:
            word_freq = Counter(text_analysis['words'])
            word_freq_no_stopwords = Counter(text_analysis['words_no_stopwords'])
            bigram_freq = Counter(text_analysis['bigrams'])
            
            top_words = word_freq.most_common(20)
            top_words_no_stopwords = word_freq_no_stopwords.most_common(20)
            top_bigrams = bigram_freq.most_common(15)
            
            return {
                'word_freq': word_freq,
                'word_freq_no_stopwords': word_freq_no_stopwords,
                'bigram_freq': bigram_freq,
                'top_words': top_words,
                'top_words_no_stopwords': top_words_no_stopwords,
                'top_bigrams': top_bigrams
            }
        except Exception as e:
            return None

    freq_analysis = analyze_frequencies(text_analysis)

    # Visualizations
    if text_analysis and freq_analysis:
        st.subheader("Word Cloud")
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(text_analysis['words_no_stopwords']))
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        st.subheader("Word Frequency")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        chapter_df = pd.DataFrame(text_analysis['chapter_info'])
        axes[0, 0].bar(range(len(chapter_df)), chapter_df['word_count'])
        axes[0, 0].set_title('Word Count by Chapter')
        axes[0, 0].set_xlabel('Chapter Index')
        axes[0, 0].set_ylabel('Word Count')
        axes[0, 0].grid(True, alpha=0.3)
        
        top_words_df = pd.DataFrame(freq_analysis['top_words_no_stopwords'][:20], columns=['word', 'count'])
        axes[0, 1].barh(range(len(top_words_df)), top_words_df['count'])
        axes[0, 1].set_yticks(range(len(top_words_df)))
        axes[0, 1].set_yticklabels(top_words_df['word'])
        axes[0, 1].set_title('Top 20 Words (No Stopwords)')
        axes[0, 1].set_xlabel('Frequency')
        
        top_bigrams_df = pd.DataFrame(freq_analysis['top_bigrams'][:20], columns=['bigram', 'count'])
        axes[1, 0].barh(range(len(top_bigrams_df)), top_bigrams_df['count'])
        axes[1, 0].set_yticks(range(len(top_bigrams_df)))
        axes[1, 0].set_yticklabels(top_bigrams_df['bigram'])
        axes[1, 0].set_title('Top 20 Bigrams')
        axes[1, 0].set_xlabel('Frequency')
        
        sentence_lengths = [len(sent.split()) for sent in text_analysis['sentences']]
        axes[1, 1].hist(sentence_lengths, bins=50, alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('Sentence Length Distribution')
        axes[1, 1].set_xlabel('Words per Sentence')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
