import os
from langchain_huggingface import HuggingFaceEmbeddings

# Environment variables
MONGO_URI = os.getenv("MONGO_DB_URL")
DB_NAME = 'ask_my_document'
COLLECTION_NAME = 'book'
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:cloud")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
