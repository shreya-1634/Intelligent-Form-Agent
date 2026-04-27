import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import IntelligentFormAgent

@st.cache_resource
def load_agent():
    # Caching the agent prevents reloading the multi-GB models on every interaction
    return IntelligentFormAgent()

def main():
    st.title("📄 Intelligent Form Agent")
    st.markdown("Upload your PDF forms to extract summaries, ask questions, or perform holistic analysis.")

    # Initialize Agent
    with st.spinner("Loading NLP Models..."):
        agent = load_agent()

    # Sidebar for File Uploads
    st.sidebar.header("Upload Center")
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF files", type="pdf", accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Please upload one or more PDF files in the sidebar to begin.")
        return

    # Save uploaded files to a temporary directory for the agent to read
    temp_dir = "uploaded_pdfs"
    os.makedirs(temp_dir, exist_ok=True)
    file_paths = []
    for uploaded_file in uploaded_files:
        path = os.path.join(temp_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(path)

    # UI Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Single QA", "Summarization", "Holistic Insights"])

    with tab1:
        st.header("Ask a Question")
        target_file = st.selectbox("Select a file", [f.name for f in uploaded_files])
        question = st.text_input("Enter your question", placeholder="e.g., What is the total amount?")
        
        if st.button("Get Answer"):
            if question:
                target_path = os.path.join(temp_dir, target_file)
                result = agent.process_single_form_qa(target_path, question)
                st.success(f"**Answer:** {result.get('answer', 'N/A')}")
                st.caption(f"Confidence Score: {result.get('score', 0.0):.4f}")
            else:
                st.warning("Please enter a question.")

    with tab2:
        st.header("Generate Summary")
        sum_file = st.selectbox("Select file to summarize", [f.name for f in uploaded_files])
        if st.button("Summarize"):
            sum_path = os.path.join(temp_dir, sum_file)
            summary_list = agent.process_single_form_summary(sum_path)
            if summary_list:
                # The pipeline returns a list of dicts
                st.write(summary_list[0].get('summary_text', "No summary generated."))
            else:
                st.error("Could not generate summary.")

    with tab3:
        st.header("Holistic Analysis")
        h_question = st.text_input("Question for all files", placeholder="e.g., Are there any recurring dates?")
        if st.button("Analyze All"):
            with st.spinner("Analyzing across all documents..."):
                df_results = agent.process_multiple_forms_holistic(temp_dir, h_question)
                st.dataframe(df_results, use_container_width=True)

if __name__ == "__main__":
    main()
