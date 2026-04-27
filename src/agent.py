import logging
import os
import pandas as pd
import google.generativeai as genai
from typing import List, Dict, Any

from src.extraction import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.0-flash"

class IntelligentFormAgent:
    
    def __init__(self):
        logger.info("Initializing API-based agent...")
        # Grab the API key from the server environment
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            logger.warning("GEMINI_API_KEY is missing! App will crash when making requests.")
            
        genai.configure(api_key=api_key)
        # Using flash because it is free, extremely fast, and handles large documents easily
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Agent initialized successfully.")

    def process_single_form_qa(self, pdf_path: str, question: str) -> Dict[str, Any]:
        logger.info(f"Processing QA for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            return {"answer": "No text could be extracted from this PDF.", "score": 0.0}
            
        prompt = f"""
        You are an intelligent document assistant. Use the following document text to answer the question.
        
        Document Text:
        {context[:15000]} 
        
        Question: {question}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # We return a score of 1.0 because generative APIs don't use extractive confidence scores
            return {"answer": response.text.strip(), "score": 1.0}
        except Exception as e:
            logger.error(f"API Error: {e}")
            return {"answer": f"Error communicating with AI: {e}", "score": 0.0}

    def process_single_form_summary(self, pdf_path: str, min_length: int = 30, max_length: int = 150) -> List[Dict[str, str]]:
        logger.info(f"Processing summary for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            return []
            
        prompt = f"""
        Please provide a concise summary of the following document. Keep it professional.
        
        Document Text:
        {context[:15000]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Returning as a list of dicts to perfectly match your Streamlit UI's expected format
            return [{"summary_text": response.text.strip()}]
        except Exception as e:
            logger.error(f"API Error: {e}")
            return []

    def process_multiple_forms_holistic(self, pdf_directory: str, question: str) -> pd.DataFrame:
        logger.info(f"Processing holistic insights...")
        
        try:
            pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
        except FileNotFoundError:
            return pd.DataFrame(columns=["file", "question", "answer", "score"])
            
        if not pdf_files:
            return pd.DataFrame(columns=["file", "question", "answer", "score"])

        results = []
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            qa_result = self.process_single_form_qa(file_path, question)
            
            results.append({
                "file": pdf_file,
                "question": question,
                "answer": qa_result.get("answer", "N/A"),
                "score": qa_result.get("score", 0.0)
            })
        
        return pd.DataFrame(results)
