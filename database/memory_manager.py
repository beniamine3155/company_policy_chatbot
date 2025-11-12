import os
import json
from typing import Dict, List, Any
from utils.logger import logger
from utils.exceptions import CustomException

class ConversationMemory:
    """Manages in-memory conversation history."""


    def __init__(self, storage_path: str = "conversation_memory.json"):
        self.storage_path = storage_path
        self.conversations = self.load_conversations()


    def load_conversations(self) -> Dict[str, List[Dict[str, str]]]:
        """Load conversations from storage."""
        
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Failed to load conversations: {str(e)}")
            return {}
    

    def save_conversations(self) -> None:
        """Save conversations to storage."""
        
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversations: {str(e)}")
    
    def add_message(self, session_id: str, user_message: str, assistant_message: str) -> None:
        """Add a message to conversation history."""
        
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            'user': user_message,
            'assistant': assistant_message
        })
        
        # Keep only last 20 messages per session
        if len(self.conversations[session_id]) > 20:
            self.conversations[session_id] = self.conversations[session_id][-20:]
        
        self.save_conversations()
        logger.info(f"Added message to session: {session_id}")

    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        return self.conversations.get(session_id, [])
    

    def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        
        if session_id in self.conversations:
            del self.conversations[session_id]
            self.save_conversations()
            logger.info(f"Cleared conversation for session: {session_id}")