import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.chat_models import ChatOllama

from app.config import MONGO_URI, DB_NAME, COLLECTION_NAME, OLLAMA_MODEL, embeddings

router = APIRouter()

class UploadResponse(BaseModel):
    filename: str
    message: str

def custom_metadata_tagger(documents):
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.1)
    tagged_documents = []
    
    for doc in documents:
        prompt = f"""
Extract metadata from this document content and return ONLY a JSON object with these fields:
- title: a concise summary (string)
- keywords: 3-5 relevant terms (array of strings)
- hasCode: true if contains programming code, false otherwise (boolean)

Document content:
{doc.page_content[:500]}...

Return only the JSON object, no other text:
"""
        
        try:
            response = llm.invoke(prompt)
            metadata = json.loads(response.content.strip())
            if all(key in metadata for key in ["title", "keywords", "hasCode"]):
                doc.metadata.update(metadata)
            else:
                doc.metadata.update({"title": "Unknown", "keywords": [], "hasCode": False})
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            doc.metadata.update({"title": "Unknown", "keywords": [], "hasCode": False})
        
        tagged_documents.append(doc)
    
    return tagged_documents

@router.post("/upload/", response_model=UploadResponse)
async def upload_document(files: List[UploadFile] = File(...)):
    processed_files = []
    temp_files = []
    
    try:
        all_docs = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
        
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"Invalid file type for {file.filename}. Only PDFs are supported.")
            
            # Sanitize filename to prevent path traversal
            safe_filename = os.path.basename(file.filename).replace("..", "")
            temp_file_path = f"/tmp/{safe_filename}"
            temp_files.append(temp_file_path)
            
            with open(temp_file_path, "wb") as f:
                f.write(await file.read())
            
            loader = PyPDFLoader(temp_file_path)
            pages = loader.load()
            
            cleaned_pages = [page for page in pages if len(page.page_content.split(" ")) > 20]
            print('cleaned_pages', cleaned_pages)
            tagged_docs = custom_metadata_tagger(cleaned_pages)
            print('tagged_docs', tagged_docs)
            docs = text_splitter.split_documents(tagged_docs)
            print('docs', docs)
            all_docs.extend(docs)
            processed_files.append(file.filename)
        
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            MONGO_URI,
            f"{DB_NAME}.{COLLECTION_NAME}",
            embeddings,
            index_name="vector_index"
        )
        vector_store.add_documents(all_docs)
        
        return UploadResponse(
            filename=", ".join(processed_files),
            message=f"{len(processed_files)} documents processed and ingested successfully.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)