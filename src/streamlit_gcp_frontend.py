import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List
import os
from src.eda_page import show_eda_page

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")  # Local API in same container

# Page configuration
st.set_page_config(
    page_title="Closed Book QA - GCP",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .source-card {
        background-color: #f8f9fa;
        color: #333;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "book_id" not in st.session_state:
    st.session_state.book_id = "debt_crisis"
if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"

# Header
st.markdown('<div class="main-header">📚 Closed Book QA - GCP</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Status Check
    st.subheader("🔗 API Status")
    if st.button("Check API Health"):
        try:
            response = requests.get(f"{API_URL}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                st.session_state.api_status = "healthy"
                st.success("✅ API is healthy")
                st.json(data)
            else:
                st.session_state.api_status = "unhealthy"
                st.error("❌ API is unhealthy")
        except Exception as e:
            st.session_state.api_status = "error"
            st.error(f"❌ Cannot connect to API: {str(e)}")
    
    # Book Selection
    st.subheader("📖 Book Selection")
    book_map = {
        "Big Debt Crisis by Ray Dalio": "debt_crisis",
        "Saving Capitalism from the Capitalists by Raghuram Rajan": "capitalism",
    }
    book_choice = st.selectbox(
        "Choose a book:",
        options=list(book_map.keys()),
        index=0 if st.session_state.book_id == "debt_crisis" else 1,
    )
    st.session_state.book_id = book_map[book_choice]
    
    # API Configuration
    st.subheader("🔧 API Configuration")
    st.info(f"API URL: {API_URL}")
    
    # Clear Chat
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # View EDA
    if st.button("📊 View EDA"):
        st.query_params.page = "eda"
        st.rerun()

# Main app logic
query_params = st.query_params
page = st.query_params.get("page")

if page == "eda":
    # Use API-backed EDA on GCP to prevent heavy compute in the UI process
    show_eda_page(use_api=True, api_url=API_URL)
else:
    # Main Chat Interface
    st.header(f"💬 Querying: *{book_choice}*")

    # Display chat history
    for message in st.session_state.messages:
        if message.get("book_id") == st.session_state.book_id:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>Source {source['rank']}</strong><br>
                                <em>Chapter: {source['metadata'].get('chapter', 'N/A')}</em><br>
                                <em>PDF Page: {source['metadata'].get('pdf_page', 'N/A')}</em><br>
                                <em>Book ID: {source['metadata'].get('book_id', 'N/A')}</em><br>
                                <p>Content: {source['content']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Display processing time if available
                if "processing_time" in message:
                    st.caption(f"⏱️ Processing time: {message['processing_time']:.2f}s")

    # Handle new user input
    if prompt := st.chat_input(f"Ask a question about {book_choice}..."):
        # Add user message to history
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "book_id": st.session_state.book_id}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Prepare request
                status_text.text("🔄 Preparing request...")
                progress_bar.progress(25)
                
                request_data = {
                    "question": prompt,
                    "book_id": st.session_state.book_id
                }
                
                # Step 2: Send request to API
                status_text.text("🚀 Sending request to Backend Server...")
                progress_bar.progress(50)
                
                response = requests.post(
                    f"{API_URL}/api/ask",
                    json=request_data,
                    timeout=60  # 60 second timeout
                )
                
                progress_bar.progress(75)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display answer
                    if data["status"] == "success":
                        st.markdown(data["answer"])
                        
                        # Display sources
                        if data["sources"]:
                            with st.expander("📚 Sources"):
                                for source in data["sources"]:
                                    st.markdown(f"""
                                    <div class="source-card">
                                        <strong>Source {source['rank']}</strong><br>
                                        <em>Chapter: {source['metadata'].get('chapter', 'N/A')}</em><br>
                                        <em>PDF Page: {source['metadata'].get('pdf_page', 'N/A')}</em><br>
                                        <em>Book ID: {source['metadata'].get('book_id', 'N/A')}</em><br>
                                        <p>Content: {source['content']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Display processing time
                        st.caption(f"⏱️ Processing time: {data['processing_time']:.2f}s")
                        
                        # Add assistant message to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["answer"],
                            "sources": data["sources"],
                            "processing_time": data["processing_time"],
                            "book_id": st.session_state.book_id,
                        })
                    else:
                        st.error(f"❌ API returned error: {data['answer']}")
                        
                else:
                    st.error(f"❌ API Error ({response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to API. Please check the API URL and try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: grey; font-size: small;">
        <p>
            Made by Saksham Hooda<br>
            <a href="https://linkedin.com/in/sakshamhooda" target="_blank">linkedin.com/in/sakshamhooda</a> || 
            <a href="https://github.com/sakshamhooda" target="_blank">github.com/sakshamhooda</a><br>
            +91-8222884855 || hooda.saksham@gmail.com
        </p>
        <p><b>For R Bhargava & Associates</b></p>
        <p><em>Powered by FastAPI + Google Cloud Platform</em></p>
    </div>
    """,
    unsafe_allow_html=True
)
