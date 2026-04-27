# Intelligent-Form-Agent
An NLP agent to read, extract, and explain forms.
An AI-powered document analysis dashboard built with Streamlit and the Google Gemini API. This application allows users to upload multiple PDF documents, generate instant professional summaries, extract specific data points via Q&A, and perform holistic comparative analysis across batches of files.

Built with a focus on memory efficiency and resilience, this agent utilizes lightweight API calls and exponential backoff to handle large document sets without crashing serverless deployment platforms.


## ✨ Features

* **🔍 Single Document Q&A:** Ask targeted questions (e.g., "What are the core job requirements?", "Who is the invoice billed to?") and get precise, generative answers based on the document's extracted context.
* **📝 Automated Summarization:** Instantly generate clean, professional summaries of lengthy PDFs to quickly grasp key information without reading pages of text.
* **📊 Holistic Insights:** Ask a single question across an entire batch of uploaded PDFs simultaneously. Results are aggregated into a clean, easy-to-read tabular DataFrame—perfect for cross-referencing resumes, invoices, or financial reports.
* **🛡️ Production-Ready Reliability:** Includes built-in exponential backoff and request pacing to seamlessly handle API rate limits (`429 RESOURCE_EXHAUSTED`) during bulk document processing.

## 🛠️ Tech Stack
**Frontend & Framework**
* Streamlit

**LLM Provider**
* Google GenAI SDK (Gemini 2.0 Flash / Gemini 3 Flash)

**PDF Processing**
* PyMuPDF

**Data Manipulation**
* pandas

**Language**
* Python 3.11+

## 📂 Project Structure

```code snippet
Intelligent-Form-Agent/
│
├── data/                   # Directory for storing sample PDFs or temporary files
├── docs/                   # Additional project documentation and assets
├── notebooks/              
│   └── 01_Agent_Exploration.ipynb # Jupyter notebook for exploratory testing and model evaluation
│
├── src/                    # Main application source code
│   ├── __init__.py
│   ├── agent.py            # AI logic, Gemini API client initialization, and rate-limiting loops
│   ├── extraction.py       # PDF parsing and text extraction utility using PyMuPDF
│   └── main.py             # Streamlit frontend, UI routing, and state management
│
├── tests/                  # Unit tests to ensure extraction and AI logic reliability
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_extraction.py
│
├── .gitignore              # Rules for ignoring environment files and caches
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies for deployment
```

## ⚙️ Installation & Setup
### 1. Clone the repository:
```bash
git clone [https://github.com/shreya-1634/Intelligent-Form-Agent.git](https://github.com/shreya-1634/Intelligent-Form-Agent.git)
cd Intelligent-Form-Agent
```
### 2. Create and activate a virtual environment:
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate
```
### 3. Install the dependencies:
```bash
pip install -r requirements.txt
```
### 4. Set up Environment Variables:
Create a .env file in the root directory and add your Google Gemini API key:
```Code snippet
GEMINI_API_KEY="your_google_api_key_here"
```
### 5. Run the Application:
```bash
streamlit run src/main.py
```

## 🌐 Live Demo
👉 https://intelligent-form-agent-3zhzhvn4kktjgdyecvfdcn.streamlit.app/

## 🚀 Deployment (Streamlit Community Cloud)

* This app is optimized for free-tier deployments. To deploy on Streamlit Cloud:
* Push your repository to GitHub.
* Log into Streamlit Community Cloud and click "New app".
* Select your repository and set the main file path to src/main.py.
* Go to Advanced Settings (or Settings > Secrets after deployment) and input your API key:

```Ini, TOML
GEMINI_API_KEY = "your_google_api_key_here"
```
* Click Deploy.

## ⚠️ Core Architectural Decisions & Troubleshooting
1. Class-Based Agent (agent.py): The core logic is an IntelligentFormAgent class. This is a key design choice because the large NLP models are loaded once in the constructor (__init__) and then reused. This avoids the massive overhead of reloading the models every time a user asks a question.

2. Separation of Concerns: The code is strictly separated :
* extraction.py only knows how to deal with PDF files.
* agent.py only knows how to perform NLP tasks.
* main.py only knows how to handle command-line inputs. This makes the project easy to maintain and test.

3. Robust Interface (main.py): The use of argparse with sub-commands (qa, summarize, holistic) creates a clean, self-documenting, and user-friendly CLI.

Why API over Local Models? Originally prototyped with local Hugging Face transformers (which require >1.5GB RAM and caused Out-Of-Memory crashes on Streamlit Cloud), the architecture was migrated to a cloud API approach. This reduces the application's memory footprint to <100MB, ensuring instant load times and zero crashes.

Handling 429 API Errors: Free-tier AI APIs have strict Requests-Per-Minute (RPM) limits. The agent.py file includes a custom exponential backoff loop. If a batch process triggers a limit, the agent silently pauses for a few seconds before retrying, rather than failing the entire run.

## 📌 Future Improvements
* **RAG Integration (Cost Optimization):** Implement a lightweight vector database (e.g., ChromaDB) to chunk PDFs and send only relevant paragraphs to the API, drastically reducing token usage.

* **Multimodal Processing (Vision):** Upgrade the pipeline to pass page images directly to Gemini 2.0 Flash, enabling the agent to read scanned documents, charts, and handwritten forms.

* **One-Click CSV Export (Analyst Workflow):** Add Streamlit download buttons to the Holistic Insights tab, allowing users to export the generated comparison data directly to Excel or Tableau.

* **Session State Management:** Cache document uploads and chat history using Streamlit's st.session_state to enable seamless tab navigation without data loss or re-processing.

## 📧 Contact
Shreya Priyadrshni
📧 shreyamgm16@gmail.com

🔗 https://github.com/shreya-1634
