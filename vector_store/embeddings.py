import openai
from typing import List
from utils.logger import logger
from utils.exceptions import CustomException
from config import Config

class EmbeddingGenerator:
    """Handles text embedding generation using OpenAI."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.EMBEDDING_MODEL
        
        if not self.api_key:
            raise CustomException("OpenAI API key is required")
        
        openai.api_key = self.api_key

    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise CustomException(f"Failed to generate embeddings: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]
    
    