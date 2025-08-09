import base64
import io
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.eda_debt_crisis import (
    analyze_epub_structure as analyze_debt_epub,
    extract_text_content as extract_debt_text,
    analyze_frequencies as analyze_debt_frequencies
)
from src.eda_saving_capitalism import (
    analyze_epub_structure as analyze_capitalism_epub,
    extract_text_content as extract_capitalism_text,
    analyze_frequencies as analyze_capitalism_frequencies
)

matplotlib.use('Agg')

def generate_visualizations(text_analysis, freq_analysis):
    """
    Generates word cloud and frequency plots, returning them as base64 strings.
    """
    if not text_analysis or not freq_analysis:
        return None, None

    # --- Generate Word Cloud ---
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(text_analysis['words_no_stopwords']))
    fig_wordcloud, ax_wordcloud = plt.subplots()
    ax_wordcloud.imshow(wordcloud, interpolation='bilinear')
    ax_wordcloud.axis('off')
    
    wordcloud_buf = io.BytesIO()
    fig_wordcloud.savefig(wordcloud_buf, format='png', bbox_inches='tight')
    wordcloud_b64 = base64.b64encode(wordcloud_buf.getvalue()).decode('utf-8')
    plt.close(fig_wordcloud)

    # --- Generate Frequency Plots ---
    fig_freq, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Word Count by Chapter
    chapter_df = pd.DataFrame(text_analysis['chapter_info'])
    axes[0, 0].bar(range(len(chapter_df)), chapter_df['word_count'])
    axes[0, 0].set_title('Word Count by Chapter')
    axes[0, 0].set_xlabel('Chapter Index')
    axes[0, 0].set_ylabel('Word Count')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Top 20 Words
    top_words_df = pd.DataFrame(freq_analysis['top_words_no_stopwords'][:20], columns=['word', 'count'])
    axes[0, 1].barh(top_words_df['word'], top_words_df['count'])
    axes[0, 1].set_title('Top 20 Words (No Stopwords)')
    axes[0, 1].invert_yaxis()
    
    # Plot 3: Top 20 Bigrams
    top_bigrams_df = pd.DataFrame(freq_analysis['top_bigrams'][:20], columns=['bigram', 'count'])
    axes[1, 0].barh(top_bigrams_df['bigram'], top_bigrams_df['count'])
    axes[1, 0].set_title('Top 20 Bigrams')
    axes[1, 0].invert_yaxis()
    
    # Plot 4: Sentence Length Distribution
    sentence_lengths = [len(sent.split()) for sent in text_analysis['sentences']]
    axes[1, 1].hist(sentence_lengths, bins=50, alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Sentence Length Distribution')
    axes[1, 1].set_xlabel('Words per Sentence')
    
    plt.tight_layout()
    freq_buf = io.BytesIO()
    fig_freq.savefig(freq_buf, format='png')
    freq_b64 = base64.b64encode(freq_buf.getvalue()).decode('utf-8')
    plt.close(fig_freq)

    return wordcloud_b64, freq_b64

def generate_eda_data(book_id: str):
    """
    Main function to generate all EDA data for a given book_id.
    """
    data_dir = Path("data")
    
    if book_id == "debt_crisis":
        epub_file = data_dir / "BigDebtCrisis_RayDalio.epub"
        text_analysis = extract_debt_text(epub_file)
        freq_analysis = analyze_debt_frequencies(text_analysis)
    elif book_id == "capitalism":
        epub_file = data_dir / "SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub"
        text_analysis = extract_capitalism_text(epub_file)
        freq_analysis = analyze_capitalism_frequencies(text_analysis)
    else:
        return {"status": "error", "message": "Invalid book_id"}

    if not text_analysis or not freq_analysis:
        return {"status": "error", "message": f"Could not process book: {book_id}"}
    
    wordcloud_b64, freq_b64 = generate_visualizations(text_analysis, freq_analysis)
    
    if not wordcloud_b64 or not freq_b64:
        return {"status": "error", "message": "Failed to generate visualizations"}

    # Prepare summary stats
    summary_stats = {
        "total_words": text_analysis['total_words'],
        "unique_words": text_analysis['unique_words'],
        "total_sentences": text_analysis['total_sentences'],
        "top_word": freq_analysis['top_words_no_stopwords'][0][0] if freq_analysis['top_words_no_stopwords'] else "N/A",
        "top_word_count": freq_analysis['top_words_no_stopwords'][0][1] if freq_analysis['top_words_no_stopwords'] else 0
    }

    return {
        "status": "success",
        "word_cloud_image": wordcloud_b64,
        "frequency_plots_image": freq_b64,
        "summary_stats": summary_stats
    }
