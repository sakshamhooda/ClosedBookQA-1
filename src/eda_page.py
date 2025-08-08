import streamlit as st
from src.eda_debt_crisis import eda_big_debt_crisis
from src.eda_saving_capitalism import eda_saving_capitalism

def show_eda_page():
    st.title("Exploratory Data Analysis")

    if st.button("⬅️ Back to Chat"):
        st.query_params.page = "chat"
        st.rerun()

    book = st.selectbox("Select a book to view its EDA:", ["Big Debt Crisis", "Saving Capitalism from the Capitalists"])

    if book == "Big Debt Crisis":
        st.header("EDA for Big Debt Crisis")
        # Call the main function from the notebook's script
        eda_big_debt_crisis()
    elif book == "Saving Capitalism from the Capitalists":
        st.header("EDA for Saving Capitalism from the Capitalists")
        # Call the main function from the notebook's script
        eda_saving_capitalism()
