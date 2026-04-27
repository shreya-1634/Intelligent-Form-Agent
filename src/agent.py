import logging
import os
import pandas as pd
from google import genai
from typing import List, Dict, Any

from src.extraction import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Updated to latest stable models ---
MODEL_NAME = "gemini-2.0-flash" 

class IntelligentFormAgent:
    
    def __init__(self):
        logger.info("Initializing modern GenAI agent...")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            logger.error("GEMINI_API_KEY is missing from environment secrets!")
            
        # New SDK Client initialization
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Agent ready with model: {MODEL_NAME}")

    def process_single_form_qa(self, pdf_path: str, question: str) -> Dict[str, Any]:
        context = extract_text_from_pdf(pdf_path)
        if not context:
            return {"answer": "No text extracted.", "score": 0.0}
            
        prompt = f"Use this text to answer the question:\n\n{context[:20000]}\n\nQuestion: {question}"
        
        try:
            # Updated generation syntax
            response = self.client.models.generate_content(
                model=MODEL_NAME, 
                contents=prompt
            )
            return {"answer": response.text, "score": 1.0}
        except Exception as e:
            logger.error(f"API Error: {e}")
            return {"answer": f"Error: {e}", "score": 0.0}

    def process_single_form_summary(self, pdf_path: str) -> List[Dict[str, str]]:
        context = extract_text_from_pdf(pdf_path)
        if not context: return []
            
        prompt = f"Summarize this document clearly and professionally:\n\n{context[:20000]}"
        
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME, 
                contents=prompt
            )
            return [{"summary_text": response.text}]
        except Exception as e:
            logger.error(f"API Error: {e}")
            return []

    def process_multiple_forms_holistic(self, pdf_directory: str, question: str) -> pd.DataFrame:
        # (The logic for holistic remains the same, just calling the updated QA function)
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
        results = []
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            qa_result = self.process_single_form_qa(file_path, question)
            results.append({
                "file": pdf_file, 
                "question": question, 
                "answer": qa_result.get("answer"), 
                "score": 1.0
            })
        return pd.DataFrame(results)
