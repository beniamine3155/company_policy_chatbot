from typing import List, Any, Tuple, Dict
from utils.logger import logger
from utils.exceptions import CustomException
from vector_store.embeddings import EmbeddingGenerator
from vector_store.faiss_manager import FAISSManager
from utils.config import Config


class DocumentRetriever:
    """Handles document retrieval using vector search."""

    def __init__(self, faiss_manager: FAISSManager, embedding_generator: EmbeddingGenerator):
        self.faiss_manager = faiss_manager
        self.embedding_generator = embedding_generator

    
    def retrieve_documents(self, query: str)-> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Retrieve relevant documents for a given query."""

        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)

            # vector store search
            scores, vector_results = self.faiss_manager.search(query_embedding)
            logger.info(f"Retrieved {len(vector_results)} documents for the query")
            return vector_results

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise CustomException(f"Retrieval failed: {str(e)}")
