import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context_chunks: List[Dict[str, Any]], system_prompt: str = None) -> str:
        """
        Generate a response given a prompt and context chunks.
        """
        pass

class MockLLMProvider(BaseLLMProvider):
    def generate_response(self, prompt: str, context_chunks: List[Dict[str, Any]], system_prompt: str = None) -> str:
        # For local dev without API keys
        return f"[MOCK GENERATION]\n\nBased on the {len(context_chunks)} chunks provided, here is the answer to: '{prompt}'\n\nThe context indicates this is a test document."

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        except ImportError:
            raise ImportError("Please install openai package to use OpenAILLMProvider")

    def generate_response(self, prompt: str, context_chunks: List[Dict[str, Any]], system_prompt: str = None) -> str:
        if not system_prompt:
            system_prompt = "You are a helpful AI assistant answering questions based on provided document context."
            
        context_text = "\n\n".join([f"--- Context Chunk ---\n{c['text']}" for c in context_chunks])
        
        full_prompt = f"Context Information:\n{context_text}\n\nUser Question: {prompt}\n\nPlease answer the question based only on the provided context."

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content

def get_llm_provider() -> BaseLLMProvider:
    from django.conf import settings
    if getattr(settings, 'USE_MOCK_LLM', True):
        return MockLLMProvider()
    return OpenAILLMProvider()
