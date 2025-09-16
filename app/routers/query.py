from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.config import MONGO_URI, DB_NAME, COLLECTION_NAME, OLLAMA_MODEL, embeddings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@router.post("/query/", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            MONGO_URI,
            f"{DB_NAME}.{COLLECTION_NAME}",
            embeddings,
            index_name="vector_index"
        )
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

        retrieve = {
            "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])), 
            "question": RunnablePassthrough()
        }

        template = """
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Do not answer the question if there is no given context.
        Do not answer the question if it is not related to the context.
        Do not give recommendations to anything other than MongoDB.
        Context:
        {context}
        Question: {question}
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        response_format = StrOutputParser()
        rag_chain = (
            retrieve
            | prompt
            | llm
            | response_format
        )
        
        answer = rag_chain.invoke(request.query)
        return QueryResponse(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during query processing: {str(e)}")