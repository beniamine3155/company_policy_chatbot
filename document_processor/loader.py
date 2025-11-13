import os
import pandas as pd
from typing import List, Dict, Any

from pypdf import PdfReader
from docx import Document

from utils.logger import logger
from utils.exceptions import CustomException


class DocumentLoader:
    """Handles loading of various document types"""

    def __init__(self):
        self.supported_extensions = {
            ".txt": self._load_txt,
            ".pdf": self._load_pdf,
            ".csv": self._load_csv,
            ".docx": self._load_docx,
        }

    
    def load_documents(self, file_paths: List[str])-> Dict[str, Any]:
        """Load multiple documents and return their contents"""
        documents = []
        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    continue

                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in self.supported_extensions:
                    logger.error(f"Unsupported file type: {file_ext}")
                    continue

                load_fun = self.supported_extensions[file_ext]
                content = load_fun(file_path)

                documents.append({
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "content": content,
                    "file_type": file_ext
                })

                logger.info(f"Successfully loaded: {file_path}")

            except Exception as e:
                logger.error(f"Error occurs {file_path}: {e}")
                raise CustomException(f"Failed to load {file_path}: {e}")
            
        return documents

    # _method_name use for internal use within the class
    def _load_txt(self, file_path: str)-> str:
        """Load text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
            
        except Exception as e:
            logger.error(f"Error occurs {file_path}: {e}")
            raise CustomException(f"Failed to load text file {file_path}: {e}")


    def _load_pdf(self, file_path: str) -> str:
        """Load PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error occurs {file_path}: {e}")
            raise CustomException(f"Failed to load PDF file {file_path}: {e}")


    def _load_docx(self, file_path: str)-> str:
        """Load DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error occurs {file_path}: {e}")
            raise CustomException(f"Failed to load DOCX file {file_path}: {e}")


    def _load_csv(self, file_path: str) -> str:
        """Load CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            logger.error(f"Error occurs {file_path}: {e}")
            raise CustomException(f"Failed to load CSV file {file_path}: {e}")
