# Multi-Document Q&A System with MongoDB

A RAG (Retrieval-Augmented Generation) system that allows users to upload PDF documents and ask questions about their content using MongoDB Atlas Vector Search.

## Features

- **Document Upload**: Upload multiple PDF files with automatic metadata extraction
- **Intelligent Querying**: Ask questions about uploaded documents using Ollama LLM
- **Vector Search**: MongoDB Atlas Vector Search for semantic document retrieval
- **Metadata Tagging**: Automatic extraction of title, keywords, and code detection
- **Web Interface**: Streamlit frontend for easy interaction

## Architecture

```
├── app/                    # FastAPI Backend
│   ├── main.py            # Main FastAPI application
│   ├── config.py          # Shared configuration and dependencies
│   └── routers/           # API routers
│       ├── __init__.py    # Empty package file
│       ├── upload.py      # Document upload endpoints
│       └── query.py       # Document query endpoints
├── frontend/              # Streamlit Frontend
│   └── streamlit_app.py   # Web interface
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (create this)
└── .gitignore            # Git ignore file
```

## Setup

### Prerequisites

- Python 3.8+
- MongoDB Atlas account with Vector Search enabled
- Ollama installed locally

### Environment Variables

Create a `.env` file:

```env
MONGO_DB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=your_database_name
COLLECTION_NAME=your_collection_name
OLLAMA_MODEL=qwen3.5:cloud"
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Ollama:
   ```bash
   ollama serve
   ollama pull qwen:4b
   ```

4. Run the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Run the frontend:
   ```bash
   streamlit run app/frontend/app.py
   ```

## Usage

1. **Upload Documents**: Use the web interface to upload PDF files
2. **Ask Questions**: Enter questions about your documents
3. **Get Answers**: Receive AI-generated responses based on document content

## API Endpoints

- `POST /upload/` - Upload multiple PDF documents
- `POST /query/` - Query documents with natural language

## Technologies

- **Backend**: FastAPI, LangChain, MongoDB Atlas Vector Search
- **Frontend**: Streamlit
- **LLM**: Ollama (qwen:4b)
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **Metadata**: Local Ollama model for automatic tagging