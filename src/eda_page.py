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
        st.header(f"EDA for {'Big Debt Crisis' if book_id=='debt_crisis' else 'Saving Capitalism from the Capitalists'}")
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

                # Visual blocks similar to notebook charts
                import pandas as pd
                import altair as alt

                # Chapter word counts bar
                if data.get("chapter_info"):
                    st.subheader("Word Count by Chapter")
                    ch_df = pd.DataFrame(data["chapter_info"])  # href, word_count
                    ch_df = ch_df.reset_index().rename(columns={"index": "chapter_index"})
                    chart = alt.Chart(ch_df).mark_bar(color="#e45756").encode(
                        x=alt.X("chapter_index:O", title="Chapter Index"),
                        y=alt.Y("word_count:Q", title="Word Count"),
                        tooltip=["chapter_index", "href", "word_count"],
                    ).properties(height=250)
                    st.altair_chart(chart, use_container_width=True)

                # Top words (no stopwords)
                if data.get("top_words_no_stopwords"):
                    st.subheader("Top 20 Words (No Stopwords)")
                    tw_df = pd.DataFrame(data["top_words_no_stopwords"], columns=["word", "count"])
                    chart = alt.Chart(tw_df).mark_bar(color="#4c78a8").encode(
                        x=alt.X("count:Q", title="Frequency"),
                        y=alt.Y("word:N", sort="-x", title=None),
                        tooltip=["word", "count"],
                    ).properties(height=300)
                    st.altair_chart(chart, use_container_width=True)

                # Top bigrams
                if data.get("top_bigrams"):
                    st.subheader("Top 15 Bigrams")
                    tb_df = pd.DataFrame(data["top_bigrams"], columns=["bigram", "count"])
                    chart = alt.Chart(tb_df).mark_bar(color="#72b7b2").encode(
                        x=alt.X("count:Q", title="Frequency"),
                        y=alt.Y("bigram:N", sort="-x", title=None),
                        tooltip=["bigram", "count"],
                    ).properties(height=300)
                    st.altair_chart(chart, use_container_width=True)

                # Sentence Length Distribution
                if data.get("sentence_length_hist"):
                    st.subheader("Sentence Length Distribution")
                    bins = data["sentence_length_hist"]["bin_edges"]
                    counts = data["sentence_length_hist"]["counts"]
                    # Build midpoints for nicer plotting
                    mids = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
                    sl_df = pd.DataFrame({"bin_mid": mids, "count": counts})
                    chart = alt.Chart(sl_df).mark_area(opacity=0.6, color="#f58518").encode(
                        x=alt.X("bin_mid:Q", title="Words per Sentence"),
                        y=alt.Y("count:Q", title="Frequency"),
                        tooltip=["bin_mid", "count"],
                    ).properties(height=250)
                    st.altair_chart(chart, use_container_width=True)

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
