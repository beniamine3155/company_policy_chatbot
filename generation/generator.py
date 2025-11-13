import openai
from typing import List, Dict, Any
from utils.logger import logger
from utils.exceptions import CustomException
from utils.config import Config


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
            # Prepare context text (shorter for speed)
            context_text = self.prepare_context_fast(context)

            # Prepare conversation history
            history_text = self.prepare_history(conversation_history)

            # System prompt that handles both policy and conversation questions
            system_message = """You are an HR assistant for company policies. 
    
            For POLICY QUESTIONS: Answer based on the provided policy context with 3-4 lines of detailed explanation.
            For CONVERSATION QUESTIONS (like "what was my last message", "what did I ask before"): Use the conversation history.
            
            If asking about previous conversation, check the history and provide details.
            If asking about policies but info not in context, say: "I don't have that information in the company policy documents. Please contact HR directly for assistance."
            
            Be professional and thorough."""

            # User message with both context and history
            user_message = f"""Policy Context: {context_text}

            Conversation History: {history_text}

            Question: {query}

            Provide a detailed answer:"""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=300  # Increased for detailed 3-4 line answers
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



    def prepare_context_fast(self, context: List[Dict[str, Any]]) -> str:
        """Prepare shorter context text for faster processing."""
        
        context_text = ""
        for doc in context[:2]:  # Only use top 2 results
            content = doc.get('metadata', {}).get('content', '')
            # Truncate content to first 300 characters for speed
            content = content[:300] + "..." if len(content) > 300 else content
            context_text += f"{content}\n\n"
        
        return context_text.strip()
    
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