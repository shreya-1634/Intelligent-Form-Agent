import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any

# Set up a basic logger
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all plain text from a PDF document, page by page."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF at {pdf_path}: {e}")
        return ""

    full_text = [] 
    logger.info(f"Extracting text from {doc.page_count} pages...")

    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text")
            full_text.append(text)
        except Exception as e:
            logger.warning(f"Failed to extract text from page {page_num}: {e}")
            
    doc.close()
    
    logger.info(f"Successfully extracted {len(''.join(full_text))} characters.")
    return "\n".join(full_text)

def extract_structured_data(pdf_path: str) -> List:
    """(Advanced) Extracts structured data from a PDF using get_text('dict')."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF at {pdf_path}: {e}")
        return [] 
        
    all_page_data = [] 
    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            page_data = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
            all_page_data.append(page_data)
        except Exception as e:
            logger.warning(f"Failed to extract dict data from page {page_num}: {e}")
    
    doc.close()
    return all_page_data
