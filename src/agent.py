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

## Local module import
from src.extraction import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Define standard models.
## SQuAD-finetuned models (BERT, RoBERTa, etc.) are standard for QA.[3]
## DistilBERT is a good, fast choice.
QA_MODEL = "distilbert-base-cased-distilled-squad"
SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"


class IntelligentFormAgent:
    ##
    ## An agent capable of reading, extracting, and explaining forms.[4]
    ## 
    ## It initializes all necessary NLP models upon creation
    ## to ensure efficient, repeated use.
    ##
    
    def __init__(self, qa_model: str = QA_MODEL, summ_model: str = SUMMARIZATION_MODEL):
        ##
        ## Initializes the agent and loads the NLP models.
        ## This is done once to avoid reloading models for every call.
        ##
        logger.info(f"Initializing agent...")
        try:
            ## Load the Question-Answering pipeline [5, 3]
            logger.info(f"Loading QA model: {qa_model}")
            self.qa_pipeline: Pipeline = pipeline("question-answering", model=qa_model)
            
            ## Load the Summarization pipeline [6, 7]
            logger.info(f"Loading Summarization model: {summ_model}")
            self.summarization_pipeline: Pipeline = pipeline("summarization", model=summ_model)
            
            logger.info("Agent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            logger.error("Please ensure you have a stable internet connection"
                         " and transformers/torch are installed.")
            raise

    def process_single_form_qa(self, pdf_path: str, question: str) -> Dict[str, Any]:
        ##
        ## Performs the first required demo: Answering a question from a single form.
        ## [1indoc]
        ##
        logger.info(f"Processing QA for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            logger.warning("No text extracted. Cannot perform QA.")
            return {"error": "No text extracted from PDF."}
            
        ## The QA pipeline takes 'question' and 'context' [8]
        result = self.qa_pipeline(question=question, context=context)
        logger.debug(f"QA Pipeline raw output: {result}")
        return result

    def process_single_form_summary(self, pdf_path: str, min_length: int = 30, max_length: int = 150) -> List]:
        ##
        ## Performs the second required demo: Generating a summary of one form.
        ## [4]
        ##
        logger.info(f"Processing summary for '{pdf_path}'...")
        context = extract_text_from_pdf(pdf_path)
        
        if not context:
            logger.warning("No text extracted. Cannot perform summarization.")
            return
        
        ## The summarization pipeline takes the context string [6]
        ## We must handle context length, as many models are limited (e.g., 1024 tokens)
        truncated_context = context[:4096] ## Truncate to a safe length
        
        result_list = self.summarization_pipeline(
            truncated_context, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        logger.debug(f"Summarization raw output: {result_list}")
        return result_list ## Pipeline returns a list with one dict

    def process_multiple_forms_holistic(self, pdf_directory: str, question: str) -> pd.DataFrame:
        ##
        ## Performs the third required demo: Providing a holistic answer
        ## across multiple forms. [4]
        ## 
        ## This implementation iterates over all PDFs in a directory, 
        ## asks the *same question* to each, and aggregates the answers 
        ## into a pandas DataFrame.[9, 10]
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

        results =  ## <-- FIX: Was an empty line
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            logger.info(f"Querying file: {pdf_file}...")
            
            ## We re-use the single-form QA method
            qa_result = self.process_single_form_qa(file_path, question)
            
            results.append({
                "file": pdf_file,
                "question": question,
                "answer": qa_result.get("answer", "N/A"),
                "score": qa_result.get("score", 0.0)
            })
        
        ## Use pandas [9, 10] to structure the aggregated results
        df = pd.DataFrame(results)
        logger.info("Holistic analysis complete.")
        return df