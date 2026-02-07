"""
AI Client implementations for GradeIt.
Supports generic interface for multiple providers.
"""

import abc
import os
from typing import Optional
import google.generativeai as genai
from anthropic import Anthropic


class AIClient(abc.ABC):
    """Abstract base class for AI providers."""
    
    @abc.abstractmethod
    def analyze_code(self, prompt: str) -> str:
        """Send prompt to AI and return response text."""
        pass


class GeminiClient(AIClient):
    """Google Gemini implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        # Disable safety filters for code analysis tasks
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

    def analyze_code(self, prompt: str) -> str:
        """Analyze code using Gemini."""
        try:
            response = self.model.generate_content(
                prompt, 
                safety_settings=self.safety_settings,
                generation_config={"response_mime_type": "application/json"}
            )
            # Check if valid text part exists
            if response.parts:
                 return response.text
                 
            # If no text, check the feedback
            return f"{{\n \"score\": 0,\n \"feedback\": \"AI Error: Response blocked. Reason: {response.prompt_feedback}\",\n \"suggestions\": [],\n \"confidence\": 0.0\n}}"

        except Exception as e:
            # Return a valid JSON error structure so the parser doesn't crash
            return f"{{\n \"score\": 0,\n \"feedback\": \"AI Error calling Gemini: {e}\",\n \"suggestions\": [],\n \"confidence\": 0.0\n}}"


class AnthropicClient(AIClient):
    """Anthropic Claude implementation."""

    def __init__(self, api_key: str, model_name: str = "claude-3-opus-20240229"):
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name

    def analyze_code(self, prompt: str) -> str:
        """Analyze code using Claude."""
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error calling Claude: {e}"


class AIClientFactory:
    """Factory for creating AI clients."""
    
    @staticmethod
    def create_client(config) -> AIClient:
        """Create client based on configuration."""
        provider = config.get('ai_provider', 'anthropic').lower()
        
        if provider == 'gemini':
            key = config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
            if not key:
                 raise ValueError("GEMINI_API_KEY not found")
            
            # Allow model override from config
            model_name = config.get('gemini_model', 'gemini-2.0-flash')
            return GeminiClient(key, model_name)
            
        elif provider == 'anthropic':
             key = config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
             if not key:
                  raise ValueError("ANTHROPIC_API_KEY not found")
             return AnthropicClient(key)
             
        raise ValueError(f"Unknown AI provider: {provider}")
