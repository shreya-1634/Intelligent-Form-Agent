import logging
import os
import time
import random
import pandas as pd
from google import genai
from typing import List, Dict, Any

from src.extraction import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Using the ultra-fast preview model
MODEL_NAME = "gemini-2.0-flash" 

class IntelligentFormAgent:
    
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("API Key missing!")
        self.client = genai.Client(api_key=api_key)

    def _generate_with_retry(self, prompt: str, max_retries: int = 3):
        """Helper to handle 429 errors by waiting and retrying."""
        for attempt in range(max_retries):
            try:
                return self.client.models.generate_content(
                    model=MODEL_NAME, 
                    contents=prompt
                )
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    # Wait 5s, 10s, etc. with a bit of random 'jitter'
                    sleep_time = (attempt + 1) * 5 + random.random()
                    logger.warning(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    raise e

    def process_single_form_qa(self, pdf_path: str, question: str) -> Dict[str, Any]:
        context = extract_text_from_pdf(pdf_path)
        if not context: return {"answer": "No text found.", "score": 0.0}
        
        prompt = f"Using this document text, answer concisely: {question}\n\nText: {context[:20000]}"
        
        try:
            response = self._generate_with_retry(prompt)
            return {"answer": response.text, "score": 1.0}
        except Exception as e:
            return {"answer": f"API is busy. Please wait a minute and try again.", "score": 0.0}

    def process_single_form_summary(self, pdf_path: str) -> List[Dict[str, str]]:
        context = extract_text_from_pdf(pdf_path)
        if not context: return []
        
        prompt = f"Summarize this document professionally:\n\n{context[:20000]}"
        
        try:
            response = self._generate_with_retry(prompt)
            return [{"summary_text": response.text}]
        except Exception:
            return [{"summary_text": "Summary unavailable due to rate limits."}]

    def process_multiple_forms_holistic(self, pdf_directory: str, question: str) -> pd.DataFrame:
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
        results = []
        
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            qa_result = self.process_single_form_qa(file_path, question)
            
            # Clean the asterisks ONLY for the holistic table
            clean_answer = qa_result.get("answer", "N/A").replace("**", "")
            
            results.append({
                "file": pdf_file,
                "question": question,
                "answer": clean_answer,
                "score": 1.0
            })
            # Force a 2-second gap between files to avoid triggering the 429
            time.sleep(2) 
            
        return pd.DataFrame(results)
