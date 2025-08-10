import base64
import requests
import streamlit as st
from typing import Optional
from src.eda_debt_crisis import eda_big_debt_crisis
from src.eda_saving_capitalism import eda_saving_capitalism

def show_eda_page(use_api: bool = False, api_url: Optional[str] = None):
    st.title("Exploratory Data Analysis")

    if st.button("⬅️ Back to Chat"):
        st.query_params.page = "chat"
        st.rerun()

    book = st.selectbox("Select a book to view its EDA:", ["Big Debt Crisis", "Saving Capitalism from the Capitalists"])

    if use_api and api_url:
        # Map UI choice to book_id expected by API
        book_id = "debt_crisis" if book == "Big Debt Crisis" else "capitalism"
        st.header(f"EDA (API) for {'Big Debt Crisis' if book_id=='debt_crisis' else 'Saving Capitalism from the Capitalists'}")
        with st.spinner("Computing EDA on server..."):
            try:
                resp = requests.get(
                    f"{api_url}/api/eda/summary",
                    params={"book_id": book_id, "include_wordcloud": True},
                    timeout=120,
                )
                if resp.status_code != 200:
                    st.error(f"API error {resp.status_code}: {resp.text}")
                    return
                data = resp.json()

                # Summary metrics
                cols = st.columns(3)
                cols[0].metric("Total words", f"{data['summary']['total_words']:,}")
                cols[1].metric("Unique words", f"{data['summary']['unique_words']:,}")
                cols[2].metric("Unique (no stopwords)", f"{data['summary']['unique_words_no_stopwords']:,}")

                # Wordcloud
                if data.get("wordcloud_png_base64"):
                    st.subheader("Word Cloud")
                    img_bytes = base64.b64decode(data["wordcloud_png_base64"])  # noqa: S320
                    st.image(img_bytes, caption="Top terms (no stopwords)")

                # Top words
                st.subheader("Top 20 Words (No Stopwords)")
                if data.get("top_words_no_stopwords"):
                    for word, count in data["top_words_no_stopwords"]:
                        st.write(f"{word}: {count}")

                # Top bigrams
                st.subheader("Top 15 Bigrams")
                if data.get("top_bigrams"):
                    for bigram, count in data["top_bigrams"]:
                        st.write(f"{bigram}: {count}")

                # Chapter stats
                st.subheader("Chapter Stats (word_count)")
                if data.get("chapter_info"):
                    for idx, ch in enumerate(data["chapter_info"]):
                        st.write(f"{idx+1:02d}. {ch['href']} — words: {ch['word_count']}")

            except requests.exceptions.Timeout:
                st.error("EDA request timed out. Please try again.")
            except Exception as e:
                st.error(f"EDA request failed: {e}")
        return

    # Local/in-process EDA rendering
    if book == "Big Debt Crisis":
        st.header("EDA for Big Debt Crisis")
        eda_big_debt_crisis()
    elif book == "Saving Capitalism from the Capitalists":
        st.header("EDA for Saving Capitalism from the Capitalists")
        eda_saving_capitalism()
