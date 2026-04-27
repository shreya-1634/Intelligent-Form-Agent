import streamlit as st
import pandas as pd
import os
import sys

# --- Path Fix for Streamlit Cloud ---
# This ensures Python looks in the root directory for the 'src' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import IntelligentFormAgent

# --- Page Configuration ---
st.set_page_config(page_title="Intelligent Form Agent", page_icon="📄", layout="wide")

@st.cache_resource
def load_agent():
    # Caching prevents reloading the heavy NLP models on every single button click
    return IntelligentFormAgent()

def main():
    st.title("📄 Intelligent Form Agent")
    st.markdown("Upload your PDF forms to extract summaries, ask questions, or perform holistic analysis.")

    # Initialize Agent
    with st.spinner("Loading NLP Models..."):
        agent = load_agent()

    # --- Sidebar for File Uploads ---
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
    
    # Clear the directory before saving new files to prevent overlapping data
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))

    file_paths = []
    for uploaded_file in uploaded_files:
        path = os.path.join(temp_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(path)

    # --- UI Tabs for Functionalities ---
    tab1, tab2, tab3 = st.tabs(["Single QA", "Summarization", "Holistic Insights"])
    
   # --- Tab 1: Single Form Question Answering ---
    with tab1:
        st.header("Ask a Question")
        target_file = st.selectbox("Select a file", [f.name for f in uploaded_files], key="qa_select")
        question = st.text_input("Enter your question", placeholder="e.g., What is the total amount?")
        
        if st.button("Get Answer"):
            if question:
                target_path = os.path.join(temp_dir, target_file)
                with st.spinner("Analyzing document..."):
                    
                    # ---> THIS IS THE LINE THAT WAS MISSING <---
                    result = agent.process_single_form_qa(target_path, question)
                    
                    # Check if the AI is confident in its answer
                    if result.get('score', 0.0) < 0.15:
                        st.warning("**Answer:** I could not find a clear answer in the text.")
                    else:
                        st.success(f"**Answer:** {result.get('answer', 'N/A')}")
                        
                    st.caption(f"Confidence Score: {result.get('score', 0.0):.4f}")
            else:
                st.warning("Please enter a question.")
    # --- Tab 2: Summarization ---
    with tab2:
        st.header("Generate Summary")
        sum_file = st.selectbox("Select file to summarize", [f.name for f in uploaded_files], key="sum_select")
        
        if st.button("Summarize"):
            sum_path = os.path.join(temp_dir, sum_file)
            with st.spinner("Generating summary..."):
                summary_list = agent.process_single_form_summary(sum_path)
                if summary_list and len(summary_list) > 0:
                    # The summarization pipeline returns a list containing a dictionary
                    st.write(summary_list[0].get('summary_text', "No summary generated."))
                else:
                    st.error("Could not generate summary. Ensure the document contains extractable text.")

    # --- Tab 3: Holistic Analysis Across Multiple Forms ---
    with tab3:
        st.header("Holistic Analysis")
        st.write("Ask a single question across all uploaded documents simultaneously.")
        h_question = st.text_input("Question for all files", placeholder="e.g., Are there any recurring dates?", key="h_quest")
        
        if st.button("Analyze All"):
            if h_question:
                with st.spinner(f"Analyzing {len(uploaded_files)} documents..."):
                    df_results = agent.process_multiple_forms_holistic(temp_dir, h_question)
                    if not df_results.empty:
                        st.dataframe(df_results, use_container_width=True)
                    else:
                        st.warning("No results found or an error occurred during analysis.")
            else:
                st.warning("Please enter a question for holistic analysis.")

if __name__ == "__main__":
    main()
