import openai
from typing import List, Dict, Any
from utils.logger import logger
from utils.exceptions import CustomException
from config import Config


class ResponseGenerator:
    """Handles text generation using OpenAI's GPT models."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL

        if not self.api_key:
            raise CustomException("OpenAI API key is required")
        
        openai.api_key = self.api_key


    def generate_response(self, query: str, context: List[Dict[str, Any]], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a response based on the query and context."""

        try:
            # Prepare contex text
            context_text = self.prepare_context(context)

            # Prepare conversation history
            history_text = self.prepare_history(conversation_history)

            # System prompt
            system_message = """You are a helpful HR assistant for company policies. 
            Answer questions based ONLY on the provided context. 
            If the answer cannot be found in the context, say so and don't make up information.
            Be concise and professional in your responses."""

            # User message with context
            user_message = f"""Context: {context_text}
            Conversation History: {history_text}
            Question: {query}
            Please provide a helpful answer based on the context above."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=500
            )
            
            answer = response.choices[0].message.content

            # Extract sources
            sources = self.extract_sources(context)

            logger.info("Successfully generated response")
            return {
                'answer': answer,
                'sources': sources,
                'model': self.model
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise CustomException(f"Response generation failed: {str(e)}")



    def prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Prepare context text from retrieved documents."""
        
        context_text = ""
        for i, doc in enumerate(context, 1):
            source = doc.get('metadata', {}).get('source', 'Unknown')
            content = doc.get('metadata', {}).get('content', '')
            score = doc.get('score', 0)
            
            context_text += f"[Source {i}: {source} (Relevance: {score:.2f})]\n{content}\n\n"
        
        return context_text.strip()
    

    def prepare_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """Prepare conversation history text."""
        
        if not conversation_history:
            return "No previous conversation."
        
        history_text = ""
        for turn in conversation_history[-5:]:  # Last 5 turns
            history_text += f"User: {turn.get('user', '')}\n"
            history_text += f"Assistant: {turn.get('assistant', '')}\n"
        
        return history_text
    

    def extract_sources(self, context: List[Dict[str, Any]]) -> List[str]:
        """Extract unique sources from context."""
        
        sources = set()
        for doc in context:
            source = doc.get('metadata', {}).get('source', 'Unknown')
            if source and source != 'Unknown':
                sources.add(source)
        
        return list(sources)