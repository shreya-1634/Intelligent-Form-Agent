##
## The Intelligent Form Agent
##
## This module defines the core IntelligentFormAgent class.
## It loads and orchestrates the NLP pipelines from transformers
## to perform QA, summarization, and holistic analysis.
##

import logging
import os
from transformers import pipeline, Pipeline
from typing import List, Dict, Any
import pandas as pd

## Local module import (This works in the package structure)
from src.extraction import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Define standard models.
QA_MODEL = "distilbert-base-cased-distilled-squad"
SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"


class IntelligentFormAgent:
    ##
    ## An agent capable of reading, extracting, and explaining forms.
    ##
    
   def __init__(self, qa_model: str = QA_MODEL, summ_model: str = SUMMARIZATION_MODEL):
        logger.info("Initializing agent in low-memory mode...")
        try:
            # QA Pipeline: Use low_cpu_mem_usage if supported
            self.qa_pipeline = pipeline(
                "question-answering", 
                model=qa_model, 
                device=-1 # Force CPU
            )
            
            # Summarization Pipeline
            self.summarization_pipeline = pipeline(
                "summarization", 
                model=summ_model, 
                device=-1
            )
            logger.info("Agent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            raise

    def process_single_form_qa(self, pdf_path: str, question: str) -> Dict[str, Any]:
        ##
        ## Performs QA on a single form. 
        ##
        logger.info(f"Processing QA for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            logger.warning("No text extracted. Cannot perform QA.")
            return {"error": "No text extracted from PDF."}
            
        result = self.qa_pipeline(question=question, context=context)
        logger.debug(f"QA Pipeline raw output: {result}")
        return result

    def process_single_form_summary(self, pdf_path: str, min_length: int = 30, max_length: int = 150) -> List:
        ##
        ## Generates a summary of one form. 
        ##
        logger.info(f"Processing summary for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            logger.warning("No text extracted. Cannot perform summarization.")
            return ## <-- Return empty list
        
        truncated_context = context[:4096] ## Truncate to a safe length
        
        result_list = self.summarization_pipeline(
            truncated_context, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        logger.debug(f"Summarization raw output: {result_list}")
        return result_list 

    def process_multiple_forms_holistic(self, pdf_directory: str, question: str) -> pd.DataFrame:
        ##
        ## Performs holistic insights across multiple forms. 
        ##
        logger.info(f"Processing holistic insights for directory '{pdf_directory}'...")
        
        try:
            pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
        except FileNotFoundError:
            logger.error(f"Directory not found: '{pdf_directory}'")
            return pd.DataFrame(columns=["file", "question", "answer", "score"])
            
        if not pdf_files:
            logger.warning(f"No PDF files found in '{pdf_directory}'.")
            return pd.DataFrame(columns=["file", "question", "answer", "score"])

        results =  []
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            logger.info(f"Querying file: {pdf_file}...")
            
            qa_result = self.process_single_form_qa(file_path, question)
            
            results.append({
                "file": pdf_file,
                "question": question,
                "answer": qa_result.get("answer", "N/A"),
                "score": qa_result.get("score", 0.0)
            })
        
        df = pd.DataFrame(results)
        logger.info("Holistic analysis complete.")
        return df
