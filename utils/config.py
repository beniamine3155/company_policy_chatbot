import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for the project."""

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"  # Much faster than GPT-4
    EMBEDDING_MODEL = "text-embedding-ada-002"


    # Vector Store Configuration
    VECTOR_STORE_PATH = "vector_store"
    CHUNK_SIZE = 500  # Smaller chunks = faster processing
    CHUNK_OVERLAP = 100

    # Retrieval Configuration
    TOP_K_RESULTS = 2  # Fewer results = faster processing
    SIMILARITY_THRESHOLD = 0.7

    # Web Search Configuration
    ENABLE_WEB_SEARCH = True
    WEB_SEARCH_TIMEOUT = 10

    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "chatbot.log"

