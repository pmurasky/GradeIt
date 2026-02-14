"""
Tests for AI Client Factory.
"""

import pytest
from unittest.mock import Mock, patch
from src.gradeit.ai_clients import AIClientFactory, GeminiClient, AnthropicClient

class TestAIClientFactory:
    """Test AI Client Factory."""

    def test_create_gemini_client(self):
        """Test creating Gemini client."""
        config = Mock()
        config.get.side_effect = lambda k, d=None: 'gemini' if k == 'ai_provider' else 'fake_key' if k == 'gemini_api_key' else d
        
        with patch('src.gradeit.ai_clients.genai.Client'):
            client = AIClientFactory.create_client(config)
            assert isinstance(client, GeminiClient)

    def test_create_anthropic_client(self):
        """Test creating Anthropic client."""
        config = Mock()
        config.get.side_effect = lambda k, d=None: 'anthropic' if k == 'ai_provider' else 'fake_key' if k == 'anthropic_api_key' else d
        
        with patch('src.gradeit.ai_clients.Anthropic'):
            client = AIClientFactory.create_client(config)
            assert isinstance(client, AnthropicClient)

    def test_unknown_provider(self):
        """Test unknown provider error."""
        config = Mock()
        config.get.return_value = 'unknown'
        
        with pytest.raises(ValueError):
            AIClientFactory.create_client(config)
