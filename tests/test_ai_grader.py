"""
Unit tests for AI grading module.
"""

import pytest
from unittest.mock import MagicMock, Mock
from src.gradeit.ai_grader import GradingAssistant, GradingResult
from src.gradeit.ai_clients import AIClient

@pytest.fixture
def mock_client():
    """Create a mock AI client."""
    client = MagicMock(spec=AIClient)
    return client

@pytest.fixture
def assistant(mock_client):
    """Create a GradingAssistant instance."""
    return GradingAssistant(mock_client)

def test_grade_assignment_success(assistant, mock_client):
    """Test successful grading."""
    # Setup mock response
    mock_response = """
    {
        "score": 85,
        "feedback": "Good job.",
        "suggestions": ["Add comments"],
        "confidence": 0.95
    }
    """
    mock_client.analyze_code.return_value = mock_response

    # Execute
    code_files = {"main.py": "print('hello')"}
    result = assistant.grade_assignment(code_files, "Reqs")

    # Verify
    assert isinstance(result, GradingResult)
    assert result.score == 85
    assert result.feedback == "Good job."
    assert result.confidence == 0.95
    
    # Verify client call
    mock_client.analyze_code.assert_called_once()
    call_arg = mock_client.analyze_code.call_args[0][0]
    assert "Requirements" in call_arg
    assert "Student Code" in call_arg

def test_grade_assignment_scaling(assistant, mock_client):
    """Test score scaling with max_grade."""
    mock_response = """
    {
        "score": 80, 
        "feedback": "Nice",
        "confidence": 1.0
    }
    """
    mock_client.analyze_code.return_value = mock_response

    # Grade is 80/100. If max_grade is 50, score should be 40.
    result = assistant.grade_assignment({}, "Reqs", max_grade=50)

    assert result.score == 40

def test_grade_assignment_with_solution(assistant, mock_client):
    """Test grading with solution code provided."""
    mock_client.analyze_code.return_value = '{"score": 90, "feedback": "Good", "confidence": 1.0}'
    
    code = {"Main.java": "Student Code"}
    solution = {"Main.java": "Solution Code"}
    
    assistant.grade_assignment(code, "Reqs", solution_files=solution)
    
    call_arg = mock_client.analyze_code.call_args[0][0]
    assert "Reference Solution" in call_arg
    assert "Solution Code" in call_arg
    assert "Student Code" in call_arg

def test_grade_assignment_with_context(assistant, mock_client):
    """Test grading with extracted context (headers)."""
    mock_client.analyze_code.return_value = '{"score": 90, "feedback": "Good", "confidence": 1.0}'
    
    code = {"Main.java": "/* Header */ class Main {}"}
    context = {"Main.java": "/* Header */"}
    
    assistant.grade_assignment(code, "Reqs", file_context=context)
    
    call_arg = mock_client.analyze_code.call_args[0][0]
    assert "File-Specific Instructions (from headers)" in call_arg
    assert "/* Header */" in call_arg
    assert "Student Code" in call_arg


def test_grade_assignment_json_error(assistant, mock_client):
    """Test handling of invalid JSON response."""
    mock_client.analyze_code.return_value = "Invalid JSON"

    with pytest.raises(ValueError, match="Failed to parse AI response"):
        assistant.grade_assignment({}, "Reqs")
