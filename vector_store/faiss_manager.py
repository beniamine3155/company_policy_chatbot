import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Tuple

from utils.logger import logger
from utils.exceptions import CustomException
from utils.config import Config

class FAISSManager:
    """Manages FAISS vector store operations."""

    def __init__(self, index_path: str = None):
        # Use vector_store as directory, not as file prefix
        self.vector_store_dir = index_path or Config.VECTOR_STORE_PATH
        self.index_path = os.path.join(self.vector_store_dir, "vector_index")
        self.index = None
        self.metadata = []

        # Create vector_store directory if it doesn't exist
        os.makedirs(self.vector_store_dir, exist_ok=True)


    def create_index(self, embeddings: List[List[float]]) -> None:
        """Create a FAISS index from embeddings."""
        try:
            dimension = len(embeddings[0])
            self.index = faiss.IndexFlatL2(dimension) # Inner product for cosine similarity

            # Normalize embeddings for cosine similarity
            embeddings_np = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_np)
            
            # Add embeddings to the index
            self.index.add(embeddings_np)
            logger.info(f"Created FAISS index with {len(embeddings)} vectors")

        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise CustomException(f"Failed to create FAISS index: {str(e)}")

        
    def add_documents(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]])-> None:
        """Add document embeddings and metadata to the FAISS index."""

        if self.index is None:
            self.create_index(embeddings)
        else:
            try:
                embeddings_np = np.array(embeddings).astype('float32')
                faiss.normalize_L2(embeddings_np)
                self.index.add(embeddings_np)

            except Exception as e:
                logger.error(f"Error occured while adding embeddings: {str(e)}")
                raise CustomException(f"Failed to add embeddings to FAISS index: {str(e)}")
        
        self.metadata.extend(metadata)
        logger.info(f"Added {len(embeddings)} embeddings to FAISS index")

    
    def search(self, query_embedding: List[float], k:int = None) -> Tuple[List[float], List[Dict[str, Any]]]:
        """Search for similar embeddings"""

        if self.index is None:
            raise CustomException("FAISS index is not initialized")

        k = k or Config.TOP_K_RESULTS

        try:
            query_np = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query_np)

            scores, indices = self.index.search(query_np, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                # For L2 distance, lower scores mean higher similarity
                # Convert to similarity score (higher is better)
                similarity_score = 1.0 / (1.0 + score)
                
                if idx < len(self.metadata) and idx >= 0:  # Just check valid index
                    results.append({
                        'metadata': self.metadata[idx],
                        'score': float(similarity_score)
                    })

            logger.info(f"Search returned {len(results)} results")
            return scores[0].tolist(), results
            
        except Exception as e:
            logger.error(f"Error during FAISS search: {str(e)}")
            raise CustomException(f"FAISS search failed: {str(e)}")
        

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""

        if self.index is None:
            raise CustomException("FAISS index is not initialized")
        
        try:
            # Save FAISS index
            index_file = f"{self.index_path}.index"
            faiss.write_index(self.index, index_file)

            # Save metadata
            metadata_file = f"{self.index_path}.metadata"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)

            logger.info(f"Saved FAISS index to {index_file}")
            logger.info(f"Saved metadata to {metadata_file}")

        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise CustomException(f"Failed to save FAISS index: {str(e)}")
        

    def load_index(self) -> None:
        """Load index and metadata from disk."""
        
        try:
            index_file = f"{self.index_path}.index"
            metadata_file = f"{self.index_path}.metadata"
            
            if not os.path.exists(index_file) or not os.path.exists(metadata_file):
                logger.warning(f"Index files not found in {self.vector_store_dir}, creating new index")
                return
            
            self.index = faiss.read_index(index_file)
            
            with open(metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Loaded index with {len(self.metadata)} documents from {self.vector_store_dir}")
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise CustomException(f"Failed to load index: {str(e)}")

    def reset_index(self) -> None:
        """Reset the FAISS index and metadata."""
        try:
            self.index = None
            self.metadata = []
            logger.info("Reset FAISS index and metadata")
        except Exception as e:
            logger.error(f"Error resetting index: {str(e)}")
            raise CustomException(f"Failed to reset index: {str(e)}")
            
        
                                      
    
                                      
    