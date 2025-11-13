from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn
import os
import shutil

from utils.config import Config
from utils.logger import logger
from document_processor.loader import DocumentLoader
from document_processor.splitter import DocumentSplitter
from vector_store.embeddings import EmbeddingGenerator
from vector_store.faiss_manager import FAISSManager
from retrieval.retriever import DocumentRetriever
from generation.generator import ResponseGenerator
from database.memory_manager import ConversationMemory
from document_processor.process_docs import DocumentProcessor



# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str

# Initialize components
try:
    embedding_generator = EmbeddingGenerator()
    faiss_manager = FAISSManager()
    document_retriever = DocumentRetriever(faiss_manager, embedding_generator)
    response_generator = ResponseGenerator()
    conversation_memory = ConversationMemory()
    document_processor = DocumentProcessor()
    
    # Auto process documents if needed
    document_processor.auto_process_if_needed()
    
    # Load index
    try:
        faiss_manager.load_index()
        logger.info("Loaded existing vector index")
    except Exception as e:
        logger.info(f"No existing vector index found: {e}")
        
    COMPONENTS_LOADED = True
except Exception as e:
    COMPONENTS_LOADED = False
    logger.error(f"Failed to initialize components: {e}")

app = FastAPI(title="Company Policy Chatbot API")

# Setup templates
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chat messages in memory (for simple demo)
chat_messages = []

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "messages": chat_messages})

@app.post("/chat")
async def chat_message(request: Request, message: str = Form(...)):
    """Handle chat messages"""
    if not COMPONENTS_LOADED:
        return templates.TemplateResponse("chat.html", {
            "request": request, 
            "messages": chat_messages,
            "error": "System not initialized"
        })
    
    try:
        # Add user message to chat
        chat_messages.append({"role": "user", "content": message})
        
        # Get response from AI
        vector_results = document_retriever.retrieve_documents(message)
        history = conversation_memory.get_conversation_history("default")
        
        response_data = response_generator.generate_response(message, vector_results, history)
        
        # Store conversation
        conversation_memory.add_message("default", message, response_data['answer'])
        
        # Add AI response to chat
        chat_messages.append({
            "role": "assistant", 
            "content": response_data['answer'],
            "sources": response_data['sources']
        })
        
        return templates.TemplateResponse("chat.html", {
            "request": request, 
            "messages": chat_messages
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return templates.TemplateResponse("chat.html", {
            "request": request, 
            "messages": chat_messages,
            "error": f"Error: {str(e)}"
        })

@app.post("/upload")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    """Handle file uploads"""
    try:
        saved_paths = []
        for file in files:
            # Save uploaded file
            file_path = f"data/{file.filename}"
            os.makedirs("data", exist_ok=True)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)
        
        # Process the saved files
        loader = DocumentLoader()
        documents = loader.load_documents(saved_paths)
        
        if not documents:
            return templates.TemplateResponse("chat.html", {
                "request": request, 
                "messages": chat_messages,
                "error": "No valid documents found"
            })
        
        # Process documents
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        
        texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_generator.generate_embeddings(texts)
        
        metadata = [
            {
                'source': chunk['source'],
                'content': chunk['content'],
                'start_char': chunk['start_char'],
                'end_char': chunk['end_char']
            }
            for chunk in chunks
        ]
        
        faiss_manager.add_documents(embeddings, metadata)
        faiss_manager.save_index()
        
        # Add success message to chat
        chat_messages.append({
            "role": "system", 
            "content": f"Successfully processed {len(documents)} documents: {', '.join([os.path.basename(p) for p in saved_paths])}"
        })
        
        return templates.TemplateResponse("chat.html", {
            "request": request, 
            "messages": chat_messages,
            "success": f"Uploaded and processed {len(documents)} documents"
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return templates.TemplateResponse("chat.html", {
            "request": request, 
            "messages": chat_messages,
            "error": f"Upload error: {str(e)}"
        })

@app.post("/clear")
async def clear_chat(request: Request):
    """Clear chat history"""
    chat_messages.clear()
    conversation_memory.clear_conversation("default")
    return templates.TemplateResponse("chat.html", {
        "request": request, 
        "messages": chat_messages,
        "success": "Chat cleared"
    })

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )