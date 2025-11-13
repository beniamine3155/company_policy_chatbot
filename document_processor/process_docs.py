import os
import sys

# Add parent directory to path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.logger import logger
from document_processor.loader import DocumentLoader
from document_processor.splitter import DocumentSplitter
from vector_store.embeddings import EmbeddingGenerator
from vector_store.faiss_manager import FAISSManager

class DocumentProcessor:
    """Simple class to handle automatic document processing"""
    
    def __init__(self):
        self.data_folder = "data"
    
    def auto_process_if_needed(self):
        """Simple check - always process documents to keep it simple"""
        try:
            if not os.path.exists(self.data_folder):
                print("No data folder found")
                return True
                
            # Count files
            file_count = 0
            for file in os.listdir(self.data_folder):
                if file.endswith(('.txt', '.pdf', '.docx', '.csv')):
                    file_count += 1
            
            if file_count == 0:
                print("No documents found")
                return True
            
            # Always process for simplicity
            print(f"Found {file_count} documents, processing...")
            return self.process_documents()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            logger.error(f"Error: {str(e)}")
            return False
    
    def process_documents(self):
        """Process all documents in the data folder"""
        try:
            print("Starting document processing...")
            
            # Initialize components
            embedding_generator = EmbeddingGenerator()
            faiss_manager = FAISSManager()
            loader = DocumentLoader()
            splitter = DocumentSplitter()
            
            # Get all documents from data folder
            file_paths = []
            
            if os.path.exists(self.data_folder):
                for file in os.listdir(self.data_folder):
                    if file.endswith(('.txt', '.pdf', '.docx', '.csv')):
                        file_paths.append(os.path.join(self.data_folder, file))
            
            if not file_paths:
                print("No documents found in data folder!")
                return False
            
            print(f"Found {len(file_paths)} documents")
            
            # Load documents
            documents = loader.load_documents(file_paths)
            print(f"Loaded {len(documents)} documents")
            
            # Split documents
            chunks = splitter.split_documents(documents)
            print(f"Created {len(chunks)} text chunks")
            
            # Generate embeddings
            texts = [chunk['content'] for chunk in chunks]
            embeddings = embedding_generator.generate_embeddings(texts)
            print(f"Generated {len(embeddings)} embeddings")
            
            # Prepare metadata
            metadata = [
                {
                    'source': chunk['source'],
                    'content': chunk['content'],
                    'start_char': chunk.get('start_char', 0),
                    'end_char': chunk.get('end_char', len(chunk['content']))
                }
                for chunk in chunks
            ]
            
            # Add to vector store
            faiss_manager.add_documents(embeddings, metadata)
            faiss_manager.save_index()
            
            print(f"Successfully processed {len(documents)} documents into {len(chunks)} chunks!")
            
            return True
            
        except Exception as e:
            print(f"Error processing documents: {str(e)}")
            logger.error(f"Error processing documents: {str(e)}")
            return False

if __name__ == "__main__":
    # For manual processing
    processor = DocumentProcessor()
    success = processor.process_documents()
    if success:
        print("Starting the chatbot and able to ask questions!")
    else:
        print("Document processing failed.")
