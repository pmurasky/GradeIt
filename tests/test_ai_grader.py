"""
Unit tests for AI Grading components.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock
from src.gradeit.ai_grader import (
    AnthropicClient, PromptFactory, ResponseParser, GradingAssistant, GradingResult
)


class TestPromptFactory:
    """Tests for PromptFactory."""

    def test_create_system_prompt(self):
        prompt = PromptFactory.create_system_prompt()
        assert "expert Computer Science T.A." in prompt
        assert "JSON format" in prompt

    def test_create_grading_prompt(self):
        code = {"main.py": "print('hello')"}
        reqs = "Print hello"
        prompt = PromptFactory.create_grading_prompt(code, reqs)
        
        assert "Requirements:\nPrint hello" in prompt
        assert "--- main.py ---" in prompt
        assert "print('hello')" in prompt


class TestResponseParser:
    """Tests for ResponseParser."""

    def test_parse_valid_json(self):
        json_str = '{"score": 90, "feedback": "Good job", "suggestions": [], "confidence": 0.95}'
        data = ResponseParser.parse_json_response(json_str)
        assert data["score"] == 90

    def test_parse_markdown_json(self):
        json_str = '```json\n{"score": 85}\n```'
        data = ResponseParser.parse_json_response(json_str)
        assert data["score"] == 85

    def test_parse_invalid_json(self):
        with pytest.raises(ValueError):
            ResponseParser.parse_json_response("Not JSON")

    def test_create_grading_result(self):
        data = {"score": 100, "feedback": "Perfect", "suggestions": ["None"], "confidence": 1.0}
        result = ResponseParser.create_grading_result(data)
        assert isinstance(result, GradingResult)
        assert result.score == 100
        assert result.confidence == 1.0


class TestGradingAssistant:
    """Tests for GradingAssistant."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=AnthropicClient)

    def test_grade_assignment_success(self, mock_client):
        # Setup
        assistant = GradingAssistant(mock_client)
        code = {"test.py": "pass"}
        reqs = "Do nothing"
        
        # Mock response
        mock_response = json.dumps({
            "score": 80,
            "feedback": "Works",
            "suggestions": ["Add comments"],
            "confidence": 0.8
        })
        mock_client.analyze_code.return_value = mock_response
        
        # Execute
        result = assistant.grade_assignment(code, reqs)
        
        # Verify
        assert result.score == 80
        assert result.feedback == "Works"
        mock_client.analyze_code.assert_called_once()
        
    def test_grade_assignment_api_error(self, mock_client):
        assistant = GradingAssistant(mock_client)
        mock_client.analyze_code.side_effect = RuntimeError("API Down")
        
        with pytest.raises(RuntimeError):
            assistant.grade_assignment({}, "")
