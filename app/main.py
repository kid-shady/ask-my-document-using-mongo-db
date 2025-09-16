from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import upload, query

# Load environment variables from .env file
load_dotenv()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Backend for RAG application",
    description="Two endpoints to upload files and fetch the results",
    version="1.0.0",
)

# Include routers
app.include_router(upload.router, tags=["upload"])
app.include_router(query.router, tags=["query"])
