# Chatbot Application Documentation

## Overview

This is a Streamlit-based conversational chatbot application that leverages LangGraph for intelligent routing between direct LLM responses and Retrieval Augmented Generation (RAG) for document-based Q&A.

## Features

- **Smart Routing**: Automatically determines whether queries need document search or can be answered with general knowledge
- **PDF Processing**: Upload and index PDF documents with automatic duplicate detection
- **Vector Database**: Uses Chroma for efficient document embedding and retrieval
- **Multi-LLM Support**: Switch between OpenAI GPT-4 and Google Gemini
- **Chat History**: Maintains conversation history in session state
- **Table Extraction**: Automatically extracts and formats tables from PDFs

## Project Structure

```
assignment-exl/
├── app/
│   ├── __init__.py
│   └── main.py                 # Streamlit application entry point
├── src/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── graph.py            # LangGraph routing logic
│   ├── services/
│   │   ├── __init__.py
│   │   └── pdf_service.py      # PDF processing service
│   └── utils/
│       └── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration and LLM setup
├── db/                         # Vector database storage
├── tests/                      # Unit and integration tests
├── docs/                       # Documentation
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # Project readme
```

## Installation

### Prerequisites
- Python 3.9+
- pip or conda

### Setup Steps

1. **Clone/Navigate to the project**
```bash
cd e:\python_projects\assignment-exl
```

2. **Create a virtual environment (optional but recommended)**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
# For OpenAI
LLM_API=OPENAI
OPENAI_API_KEY=your_openai_api_key

# OR for Google Gemini
LLM_API=GEMINI
GOOGLE_API_KEY=your_google_api_key
```

## Running the Application

### Start the Streamlit App

From the project root directory:

```bash
streamlit run app/main.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage Guide

### 1. Uploading PDF Documents

- Use the chat input to select PDF files
- The system automatically:
  - Extracts text and tables
  - Generates embeddings
  - Stores in vector database
  - Detects and skips duplicates

### 2. Asking Questions

- Type your question in the chat input
- The system routes the query:
  - **Direct Query**: General knowledge questions answered by LLM
  - **Tool Query**: Document-related questions search the vector database

### 3. Chat History

- All messages are saved in the session
- Clear browser cache to reset history

## Architecture

### Core Components

#### 1. **config/settings.py**
- LLM and embedding model initialization
- Vector database setup
- Prompt templates

#### 2. **src/routes/graph.py**
- LangGraph workflow definition
- Routing logic (router_node, tool_node, direct_node)
- RAG chain implementation

#### 3. **src/services/pdf_service.py**
- PDF parsing and text extraction
- Document chunking
- Vector database indexing
- Duplicate detection via file hashing

#### 4. **app/main.py**
- Streamlit UI implementation
- Session state management
- Chat interface

### Workflow

```
User Input
    ↓
Router Node (Classify Query Type)
    ↓
├── Direct Node (General Knowledge) → LLM → Answer
└── Tool Node (Document Search) → RAG → Answer
    ↓
Display Answer
```

## Configuration

### LLM Selection

**OpenAI (Default)**
```env
LLM_API=OPENAI
OPENAI_API_KEY=sk-...
```

**Google Gemini**
```env
LLM_API=GEMINI
GOOGLE_API_KEY=AIza...
```

### Vector Database

- **Storage**: `./db/` directory
- **Engine**: Chroma
- **Retrieval**: Top 3 most relevant documents

### Text Chunking

- **Chunk Size**: 1500 characters
- **Chunk Overlap**: 200 characters
- **Separators**: `\n\n`, `\n`, ` `, ``

## API Documentation

### search_docs(query: str) -> str
```python
"""Search and retrieve relevant information from PDF documents using RAG."""
```
- **Parameters**: User query string
- **Returns**: LLM-generated answer based on document context

### process_pdf(file) -> int
```python
"""Process and index a PDF file into the vector database."""
```
- **Parameters**: File object containing PDF data
- **Returns**: Number of chunks added (0 if already uploaded)

### router_node(state: GraphState) -> dict
```python
"""Route queries to appropriate processing node."""
```
- **Returns**: `{"route": "tool" | "direct"}`

## Troubleshooting

### Issue: "No module named src"
**Solution**: Ensure you're running from project root and the path is added correctly.

### Issue: API Key Errors
**Solution**: Verify `.env` file exists and has correct API keys.

### Issue: Vector Database Errors
**Solution**: Delete `db/` directory to reset, then re-upload documents.

### Issue: PDF Not Processing
**Solution**: Check PDF format, ensure it's not corrupted, and retry upload.

## Dependencies

See [requirements.txt](../requirements.txt) for full list. Key packages:
- `streamlit` - UI framework
- `langgraph` - Workflow orchestration
- `langchain` - LLM framework
- `pdfplumber` - PDF extraction
- `chromadb` - Vector database

## Future Enhancements

- [ ] Web-based file upload interface
- [ ] User authentication
- [ ] Vector database persistence
- [ ] Multiple document formats (docx, txt, etc.)
- [ ] Advanced search filters
- [ ] Document summarization
- [ ] Custom LLM fine-tuning

## Support

For issues or questions, check the logs in the terminal where Streamlit is running.

## License

This project is for educational purposes.
