# Intelligent-Form-Agent
An NLP agent to read, extract, and explain forms.
This repository contains the source code for an "Intelligent Form Agent" as specified by the Autonomize AI ML Assignment. The agent is a Python-based NLP pipeline capable of processing PDF forms to extract information, answer questions, and generate summaries.

## 1. What the Intelligent Form Agent Does
This agent provides a command-line interface (CLI) to perform three core functions, as required by the assignment :
1. Question Answering (Single Form): Extracts text from a single PDF and answers a natural language question about it.
2. Summarization (Single Form): Extracts text from a single PDF and generates a concise summary.
3. Holistic Insights (Multiple Forms): Asks the same question to an entire directory of PDFs and aggregates the answers into a single table, providing a holistic view of the data.

The core of the agent is built using PyMuPDF for high-performance PDF extraction and Hugging Face transformers for the Question-Answering and Summarization models.

## 2. Full Project Structure
This repository uses a professional Python project structure to ensure a clean separation of concerns.

File-by-File Explanation

```
your_project/
├── README.md                                     \# (This file) The main project documentation explaining what the project is and how to use it.
├── requirements.txt                              \# A list of all Python dependencies (transformers, pymupdf, pandas, etc.) needed to run the project.
├── .gitignore                                    \# Tells Git which files and folders to ignore (e.g., virtual environments, cache files).

├── /src                                          \# Python dependenciesContains all the main, runnable source code for the agent.
│  ├── src/__init__                               \# An empty file that tells Python that the /src directory is a "package."
│  ├── src/extraction.py                          \# This module handles all PDF-parsing logic. It uses PyMuPDF to read a PDF file and extract its text content.
│  ├── src/agent.py                               \# This is the heart of the project. It defines the IntelligentFormAgent class.
│  ├── src/main.py                                \# The command-line interface (CLI) entry point for the project.

├── /data                                         \# A folder to store sample forms, invoices, and other test data.
│  ├── data/.gitignore                            \# A special .gitignore inside /data to prevent large or sensitive files from being committed to the repository.
│  ├── data/dummy.pdf                             \# A small, non-sensitive sample PDF used by the test suite.

├── /notebooks	                                  \# Contains Jupyter notebooks for experiments, model testing, and exploratory work.   
│   ├── notebooks/01_Agent_Exploration.ipynb	  \# An interactive notebook to test PyMuPDF extraction  and transformers pipelines  on the fly.   

├── /tests                                        \# Contains all automated tests for quality assurance.
│   ├── tests/test_extraction.py                  \# Unit Tests for the extraction.py module. It checks if the PDF parser can correctly read the dummy.pdf.
│   ├── tests/test_agent.py                       \# Integration Tests for agent.py. It uses pytest-mock.

├── /docs                                         \# A folder for supplementary documentation, such as architecture diagrams or detailed instructions.
│   ├── docs/.gitkeep	                          \# A placeholder file to ensure the empty directory is tracked by Git.
```

## 3. How to Set Up the Environment
This project uses Python 3.9+.
1. **Clone the repository:** bash git clone https://github.com/shreya-1634/Intelligent-Form-Agent.git cd Intelligent-Form-Agent
2. Create a virtual environment (recommended):
```Bash
python -m venv.venv
source.venv/bin/activate  # On macOS/Linux
```
3. Install the required dependencies: The requirements.txt file  lists all necessary libraries.   
```Bash
pip install -r requirements.txt
```
4. (First-time run only): The first time you run the agent, the transformers library will download the pre-trained NLP models (approx. 1-2 GB). This is a one-time process.

## 4. How to Run the Agent (Step-by-Step)
The agent is run from the command line using src/main.py. We provide three sub-commands: qa, summarize, and holistic.

**Prerequisite:** Place your sample PDF files into the /data directory. This repository includes data/dummy.pdf for testing.

**Demonstration 1: Answering a question from a single form**
Requirement: "Answering a question from a single form."
**Command:** Use the qa command, providing a --path to the PDF and a --question.
**Example Run:**
```Bash
python -m src.main qa --path "data/dummy.pdf" --question "What is this file?"
```

**Expected Output:**
```2023-10-27 10:30:01 - INFO - Initializing agent...
... (model loading logs)...
2023-10-27 10:30:15 - INFO - Agent initialized successfully.
2023-10-27 10:30:15 - INFO - Processing QA for 'data/dummy.pdf'...
2023-10-27 10:30:15 - INFO - Extracting text from 1 pages...
2023-10-27 10:30:15 - INFO - Successfully extracted 53 characters.
```

--- QA Result ---
```Question: What is this file?
Answer:   Dummy PDF file
Score:    0.9876
```

**Demonstration 2: Generating a summary of one form**
Requirement: "Generating a summary of one form."
**Command:** Use the summarize command, providing a --path to the PDF.
**Example Run:** (Note: dummy.pdf is too short to summarize. Use a more text-heavy PDF.)
```Bash
python -m src.main summarize --path "data/your-text-heavy-form.pdf"
```

**Expected Output:**
```... (agent initialization)...
2023-10-27 10:31:05 - INFO - Processing summary for 'data/your-text-heavy-form.pdf'...
2023-10-27 10:31:05 - INFO - Extracting text from 3 pages...
...
```

--- Summary Result ---
This document outlines the terms and conditions for the new software license agreement. Key sections include liability, user responsibilities, and payment schedules. The agreement is valid for 24 months.

**Demonstration 3: Providing a holistic answer across multiple forms**
Requirement: "Providing a holistic answer across multiple forms."
**Command:** Use the holistic command, providing a --dir to the data folder and a single question to ask all forms.
**Example Run:** (Assuming you have invoice-01.pdf and invoice-02.pdf in /data.)
```Bash
python -m src.main holistic --dir "data/" --question "What is the Total Amount?"
```

**Expected Output:**
```(The dummy.pdf will likely return a low-confidence or incorrect answer, as it does not contain an invoice total.)
... (agent initialization)...
2023-10-27 10:32:10 - INFO - Processing holistic insights for directory 'data/'...
2023-10-27 10:32:10 - INFO - Querying file: invoice-01.pdf...
...
2023-10-27 10:32:15 - INFO - Querying file: invoice-02.pdf...
...
2023-10-27 10:32:20 - INFO - Querying file: dummy.pdf...
...
2023-10-27 10:32:22 - INFO - Holistic analysis complete.

--- Holistic Analysis for Question: 'What is the Total Amount?' ---
                 file                     question       answer     score
0  invoice-01.pdf  What is the Total Amount?      $150.00  0.9912
1  invoice-02.pdf  What is the Total Amount?    $2,400.00  0.9855
2       dummy.pdf  What is the Total Amount?  Dummy PDF file  0.1034
```

## 5. How to Run Tests
The /tests directory contains a full suite of automated tests. After installing the requirements.txt, you can run all tests by simply executing pytest in your terminal.
```Bash
pytest -v
```

- tests/test_extraction.py: Runs unit tests on the extraction.py module, verifying that it can successfully read and extract text from data/dummy.pdf.

- tests/test_agent.py: Runs integration tests on the agent.py module. It uses pytest-mock to "fake" the slow, large transformers models, allowing for fast and offline testing of the agent's logic.

## 6. Design Notes & Technology Stack
This section explains the technology and design choices for the agent.   

**Technology Stack**
```**Library**         **Purpose & Justification**

transformers        Provides the state-of-the-art NLP models. It uses its pipeline API to implement Question Answering and Summarization with minimal code.

PyMuPDF             A high-performance PDF parsing library. It was chosen because it's fast and can extract text with its full structural and coordinate data.

pandas              A library for data manipulation. It is essential for the "holistic insights" requirement 1, as it's used to create the final table of answers.

pytest              The standard framework for testing in Python.

pytest-mock         A pytest plugin used to "fake" the behavior of the large, slow transformers models during testing. It makes our test suite fast and reliable.
```

**Core Architectural Decisions**

1. Class-Based Agent (agent.py): The core logic is an IntelligentFormAgent class. This is a key design choice because the large NLP models are loaded once in the constructor (__init__) and then reused. This avoids the massive overhead of reloading the models every time a user asks a question.

2. Separation of Concerns: The code is strictly separated :   
- extraction.py only knows how to deal with PDF files.
- agent.py only knows how to perform NLP tasks.
- main.py only knows how to handle command-line inputs. This makes the project easy to maintain and test.

3. Robust Interface (main.py): The use of argparse with sub-commands (qa, summarize, holistic) creates a clean, self-documenting, and user-friendly CLI.

## 7. Optional: Design Notes & Architecture
**Core Structure:** The project is structured as a Python package (/src) with a strict separation of concerns :
- extraction.py: Handles all PyMuPDF logic.
- agent.py: Contains the IntelligentFormAgent class. This class-based design allows the expensive NLP models to be loaded only once in the constructor, improving efficiency.
- main.py: Provides the argparse CLI for user interaction.

**PDF Extraction:** We use PyMuPDF as it provides access to structured data (get_text("dict")) , which is superior for form-processing than simple text extraction. See src/extraction.py's extract_structured_data function for this advanced implementation.

**NLP Models:** We use transformers pipelines as they provide a simple, state-of-the-art API for both QA (distilbert-base-cased-distilled-squad) and Summarization (sshleifer/distilbart-cnn-12-6).

## 8. Creativity Extensions
As per the assignment , the following creative additions were included:

**Holistic Analysis:** The holistic command (src/main.py) and the process_multiple_forms_holistic method (src/agent.py) directly satisfy the "holistic insights" requirement using pandas.

**Professional Repository Structure:** The project is fully packaged with a requirements.txt, .gitignore, and a structure that separates source code (/src) from tests (/tests) and experiments (/notebooks).

**Robust Testing:** The /tests directory contains a functional test suite using pytest.
- test_extraction.py: A unit test that runs the extractor on real data.
- test_agent.py: An integration test that uses pytest-mock to mock the expensive transformers models, allowing for fast and offline testing of the agent's logic.

**Exploratory Notebook:** /notebooks/01_Agent_Exploration.ipynb is provided for interactive experimentation and to visually demonstrate the underlying technology.


For any questions or inquiries, please contact:

  * Shreya Priyadrshni
  * shreyamgm16@gmail.com
  * https://github.com/shreya-1634
