import streamlit as st
import requests
import base64
from src.eda_debt_crisis import eda_big_debt_crisis
from src.eda_saving_capitalism import eda_saving_capitalism
import os

API_URL = os.getenv("API_URL", "http://localhost:8080")

def show_eda_page(mode='local'):
    """
    Displays the EDA page, fetching data either locally or from the API 
    based on the mode.
    """
    st.title("Exploratory Data Analysis")

    if st.button("⬅️ Back to Chat"):
        st.query_params.page = "chat"
        st.rerun()

    book_map = {
        "Big Debt Crisis": "debt_crisis",
        "Saving Capitalism from the Capitalists": "capitalism"
    }
    book_choice = st.selectbox("Select a book to view its EDA:", list(book_map.keys()))
    book_id = book_map[book_choice]

    if mode == 'local':
        if book_id == "debt_crisis":
            st.header("EDA for Big Debt Crisis")
            eda_big_debt_crisis()
        elif book_id == "capitalism":
            st.header("EDA for Saving Capitalism from the Capitalists")
            eda_saving_capitalism()
    else: # gcp mode
        if st.button("🚀 Generate EDA from API"):
            with st.spinner(f"Generating EDA for *{book_choice}*... This might take a minute."):
                try:
                    response = requests.get(f"{API_URL}/api/eda/{book_id}", timeout=300)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data['status'] == 'success':
                            st.header(f"EDA for {book_choice}")
                            
                            # Display summary
                            st.subheader("Summary Statistics")
                            stats = data['summary_stats']
                            st.metric("Total Words", f"{stats['total_words']:,}")
                            st.metric("Unique Words", f"{stats['unique_words']:,}")
                            st.metric("Total Sentences", f"{stats['total_sentences']:,}")
                            
                            # Display images
                            st.subheader("Word Cloud")
                            img_bytes = base64.b64decode(data['word_cloud_image'])
                            st.image(img_bytes, use_column_width=True)
                            
                            st.subheader("Frequency Plots")
                            img_bytes = base64.b64decode(data['frequency_plots_image'])
                            st.image(img_bytes, use_column_width=True)
                            
                            st.success("EDA generated successfully!")
                        else:
                            st.error(f"API Error: {data.get('message', 'Unknown error')}")
                    else:
                        st.error(f"API Request Failed with status {response.status_code}: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to the API: {e}")
