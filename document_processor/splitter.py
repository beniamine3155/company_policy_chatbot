from typing import List, Dict, Any
from utils.logger import logger
from config import Config

class DocumentSplitter:
    """Handles documents splitting into chunks"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP


    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks."""
        
        chunks = []
        for doc in documents:
            doc_chunks = self._split_text(doc['content'], doc['file_name'])
            chunks.extend(doc_chunks)
        
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks


    def _split_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            chunks.append({
                'content': chunk.strip(),
                'source': source,
                'start_char': start,
                'end_char': end
            })
            
            start += self.chunk_size - self.chunk_overlap
        
        return chunks