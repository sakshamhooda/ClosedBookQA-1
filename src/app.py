import streamlit as st
import os
import sys
from dotenv import load_dotenv
import time

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag import retrieve, generate_answer, verify_answer
from src.data_ingestion import ingest_book
from src.eda_page import show_eda_page


# -----------------------------------------------------------------------------
# App Configuration & State
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Closed Book QA for R Bhargava & Associates",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Closed Book QA for R Bhargava & Associates")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "book_id" not in st.session_state:
    st.session_state.book_id = "debt_crisis"


# -----------------------------------------------------------------------------
# Sidebar for Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
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

    st.info(
        "This app uses a RAG pipeline with Gemini to answer questions based "
        "solely on the contents of the selected book."
    )

    # Ingestion trigger
    st.header("Data Management")
    if st.button("Re-ingest Both Books"):
        with st.spinner("Ingesting 'Big Debt Crisis'..."):
            ingest_book(
                "debt_crisis",
                "data/BigDebtCrisis_RayDalio.epub",
            )
        with st.spinner("Ingesting 'Saving Capitalism'..."):
            ingest_book(
                "capitalism",
                "data/SavingCapitalismFromCapitalist_RaghuramRajan_LuigiZingales.epub",
            )
        st.success("Ingestion complete for both books.")

    # View EDA
    if st.button("📊 View EDA"):
        st.query_params.page = "eda"
        st.rerun()

# -----------------------------------------------------------------------------
# Main app logic
# -----------------------------------------------------------------------------
query_params = st.query_params
page = query_params.get("page")

if page == "eda":
    show_eda_page()
else:
    # Main Chat Interface
    st.header(f"Querying: *{book_choice}*")

    # Display chat history
    for message in st.session_state.messages:
        if message.get("book_id") == st.session_state.book_id:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message:
                    with st.expander("Sources"):
                        for i, doc in enumerate(message["sources"]):
                            st.write(f"**Source {i+1}** (Metadata: {doc.metadata})")
                            st.info(doc.page_content)


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
            with st.spinner("Thinking..."):
                passages = retrieve(prompt, st.session_state.book_id)
                answer = generate_answer(prompt, passages)
                # verification = verify_answer(answer, passages) # Optional

                st.markdown(answer)

                # Display sources
                with st.expander("Sources"):
                    for i, doc in enumerate(passages):
                        meta = doc.metadata
                        st.write(
                            f"**Source {i+1}** | "
                            f"Chapter: `{meta.get('chapter', 'N/A')}` | "
                            f"PDF Page (est.): `{meta.get('pdf_page', 'N/A')}` | "
                            f"Book ID: `{meta.get('book_id')}`"
                        )
                        st.info(doc.page_content)
                        # Future: f"PDF Page: ~{meta.get('pdf_page', 'N/A')}"

            # Add assistant message to history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": passages,
                    "book_id": st.session_state.book_id,
                }
            )

    # --- Footer ---
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
        </div>
        """,
        unsafe_allow_html=True
    )

