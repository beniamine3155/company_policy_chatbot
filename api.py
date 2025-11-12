from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

from config import Config
from utils.logger import logger
from utils.exceptions import CustomException
from document_processor.loader import DocumentLoader
from document_processor.splitter import DocumentSplitter
from vector_store.embeddings import EmbeddingGenerator
from vector_store.faiss_manager import FAISSManager
from retrieval.retriever import DocumentRetriever
from generation.generator import ResponseGenerator
from database.memory_manager import ConversationMemory


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources : List[str]
    session_id: str

class DocumentUploadResponse(BaseModel):
    message: str
    document_processed: int


# Initialize components
embedding_generator = EmbeddingGenerator()
faiss_manager = FAISSManager()
document_retriever = DocumentRetriever(faiss_manager, embedding_generator)
response_generator = ResponseGenerator()
conversation_memory = ConversationMemory()


# Load existing index
try:
    faiss_manager.load_index()
    logger.info("Loaded existing vector index")
except:
    logger.info("No existing vector index found")

app = FastAPI(title="Company Policy Chatbot API")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """chat endpoint for policy questions"""
    try:
        # Retrieve relevant documens
        vector_results = document_retriever.retrieve_documents(request.message)

        # Combine result
        all_results = vector_results 
        
        # Get conversation history
        history = conversation_memory.get_conversation_history(request.session_id)
        
        # Generate response
        response_data = response_generator.generate_response(
            request.message, all_results, history
        )
        
        # Store conversation
        conversation_memory.add_message(
            request.session_id, request.message, response_data['answer']
        )

        return ChatResponse(
            answer=response_data['answer'],
            sources=response_data['sources'],
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    



@app.post("/upload-documents")
async def upload_documents(file_paths: List[str]):
    """Upload and process documents."""
    
    try:
        # Load documents
        loader = DocumentLoader()
        documents = loader.load_documents(file_paths)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid documents found")
        
        # Split documents
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        
        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_generator.generate_embeddings(texts)
        
        # Prepare metadata
        metadata = [
            {
                'source': chunk['source'],
                'content': chunk['content'],
                'start_char': chunk['start_char'],
                'end_char': chunk['end_char']
            }
            for chunk in chunks
        ]
        
        # Add to vector store
        faiss_manager.add_documents(embeddings, metadata)
        faiss_manager.save_index()
        
        return DocumentUploadResponse(
            message="Documents processed successfully",
            documents_processed=len(documents)
        )
    
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    



@app.get("/conversation-history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    
    try:
        history = conversation_memory.get_conversation_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@app.delete("/conversation-history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    
    try:
        conversation_memory.clear_conversation(session_id)
        return {"message": f"Conversation history cleared for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": Config.OPENAI_MODEL}

if __name__ == "__main__":
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)

