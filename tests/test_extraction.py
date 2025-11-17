##
## Unit tests for the extraction.py module
##
## This test uses pytest to validate the PDF extraction.
## It requires a sample PDF file 'data/dummy.pdf' to be present.
##

import pytest
import os
from src.extraction import extract_text_from_pdf, extract_structured_data

## We define a fixture for the path to our test data
@pytest.fixture
def sample_pdf_path():
    path = "data/dummy.pdf"
    if not os.path.exists(path):
        ## Create a dummy pdf if it doesn't exist, for the test to run
        try:
            import fitz
            os.makedirs(os.path.dirname(path), exist_ok=True)
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 72), "Dummy PDF file for testing.")
            page.insert_text((50, 92), "The Total Amount for this invoice is $150.00.")
            doc.save(path)
            doc.close()
        except ImportError:
            pytest.skip("PyMuPDF not installed, but required to create dummy test file.")
        except Exception:
             pytest.skip("Test data 'data/dummy.pdf' not found and could not be created.")
    return path

def test_extract_text_not_empty(sample_pdf_path):
    ##
    ## Tests that extract_text_from_pdf returns a non-empty string
    ## for a valid PDF.
    ##
    text = extract_text_from_pdf(sample_pdf_path)
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Dummy PDF file" in text

def test_extract_structured_data_not_empty(sample_pdf_path):
    ##
    ## Tests that the advanced extract_structured_data function
    ## also returns a valid, non-empty data structure.
    ##
    data = extract_structured_data(sample_pdf_path)
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0  ## Should have one entry per page
    assert "blocks" in data ## Check for expected PyMuPDF dict structure [1, 3, 2]

def test_extract_text_file_not_found():
    ## Tests that the extractor handles a missing file gracefully.
    text = extract_text_from_pdf("non_existent_file.pdf")
    assert text == ""