"""
AI Client implementations for GradeIt.
Supports generic interface for multiple providers.
"""

import abc
import os
from typing import Optional, List
from google import genai
from google.genai import types
from anthropic import Anthropic
from openai import OpenAI


class AIClient(abc.ABC):
    """Abstract base class for AI providers."""
    
    @abc.abstractmethod
    def analyze_code(self, prompt: str) -> str:
        """Send prompt to AI and return response text."""
        pass


class GeminiClient(AIClient):
    """Google Gemini implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # Disable safety filters for code analysis tasks
        self.safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
        ]

    def analyze_code(self, prompt: str) -> str:
        """Analyze code using Gemini."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=self.safety_settings,
                    response_mime_type="application/json"
                )
            )
            # Check if valid text part exists
            if response.text:
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
            # Return a valid JSON error structure
            return f'{{\n "score": 0,\n "feedback": "AI Error calling Claude: {e}",\n "suggestions": [],\n "confidence": 0.0\n}}'


class OpenAIClient(AIClient):
    """OpenAI GPT implementation."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def analyze_code(self, prompt: str) -> str:
        """Analyze code using OpenAI GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a code grading assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            # Return a valid JSON error structure
            return f'{{\n "score": 0,\n "feedback": "AI Error calling OpenAI: {e}",\n "suggestions": [],\n "confidence": 0.0\n}}'


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
             model_name = config.get('anthropic_model', 'claude-3-5-sonnet-20241022')
             return AnthropicClient(key, model_name)
        
        elif provider == 'openai':
             key = config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
             if not key:
                  raise ValueError("OPENAI_API_KEY not found")
             model_name = config.get('openai_model', 'gpt-4o-mini')
             return OpenAIClient(key, model_name)
             
        raise ValueError(f"Unknown AI provider: {provider}")
    
    @staticmethod
    def create_fallback_clients(config) -> List[AIClient]:
        """Create a list of AI clients in fallback order based on configuration."""
        clients = []
        
        # Get the ordered list of providers from config
        providers_str = config.get('ai_providers_fallback', 'gemini,anthropic,openai')
        providers = [p.strip().lower() for p in providers_str.split(',')]
        
        # Store original provider setting
        original_provider = config.get('ai_provider', 'gemini')
        
        for provider in providers:
            try:
                # Temporarily set the provider in the config
                config.config['ai_provider'] = provider
                client = AIClientFactory.create_client(config)
                clients.append(client)
            except ValueError as e:
                # Skip providers without API keys
                print(f"Skipping {provider}: {e}")
                continue
            except Exception as e:
                # Skip providers with other errors
                print(f"Skipping {provider}: {e}")
                continue
        
        # Restore original provider setting
        config.config['ai_provider'] = original_provider
        
        if not clients:
            raise ValueError("No valid AI providers configured. Please set at least one API key.")
        
        return clients


class FallbackAIClient(AIClient):
    """AI Client that automatically falls back to alternative providers on quota errors."""
    
    def __init__(self, clients: List[AIClient]):
        if not clients:
            raise ValueError("At least one AI client must be provided")
        self.clients = clients
        self.current_index = 0
    
    def analyze_code(self, prompt: str) -> str:
        """Try each client in order until one succeeds."""
        last_error = None
        
        for i, client in enumerate(self.clients):
            try:
                result = client.analyze_code(prompt)
                
                # Check if the result indicates a quota/rate limit error
                if self._is_quota_error(result):
                    print(f"⚠️  Quota limit hit for {client.__class__.__name__}, trying next provider...")
                    last_error = result
                    continue
                
                # Success! Update current index for next time
                if i != self.current_index:
                    print(f"✓ Switched to {client.__class__.__name__}")
                    self.current_index = i
                
                return result
                
            except Exception as e:
                print(f"⚠️  Error with {client.__class__.__name__}: {e}")
                last_error = str(e)
                continue
        
        # All clients failed
        return f'{{\n "score": 0,\n "feedback": "All AI providers failed. Last error: {last_error}",\n "suggestions": [],\n "confidence": 0.0\n}}'
    
    def _is_quota_error(self, result: str) -> bool:
        """Check if the result indicates a quota or rate limit error."""
        quota_indicators = [
            '429',
            'RESOURCE_EXHAUSTED',
            'quota',
            'rate limit',
            'Rate limit',
            'exceeded your current quota'
        ]
        return any(indicator in result for indicator in quota_indicators)
