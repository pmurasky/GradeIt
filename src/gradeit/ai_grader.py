"""
AI Grading components for GradeIt.
Handles interaction with Anthropic/Claude for code analysis.
"""

import json
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from anthropic import Anthropic, APIError


@dataclass
class GradingResult:
    """Result of AI grading analysis."""
    score: int
    feedback: str
    suggestions: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "feedback": self.feedback,
            "suggestions": self.suggestions,
            "confidence": self.confidence
        }


class AnthropicClient:
    """Wrapper for Anthropic API interaction."""
    
    def __init__(self, api_key: str | None = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def analyze_code(self, system_prompt: str, user_prompt: str, model: str = "claude-3-sonnet-20240229") -> str:
        """Send code to Claude for analysis."""
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return message.content[0].text
        except APIError as e:
            raise RuntimeError(f"Anthropic API Error: {e}") from e


class PromptFactory:
    """Generates prompts for AI analysis."""
    
    @staticmethod
    def create_system_prompt() -> str:
        """Create the system prompt defining the AI persona."""
        return (
            "You are an expert Computer Science T.A. grading student assignments.\n"
            "Analyze the code for correctness, style, and best practices.\n"
            "Provide output in strict JSON format with keys: "
            "'score' (0-100), 'feedback' (string), 'suggestions' (list of strings), 'confidence' (0.0-1.0).\n"
            "Do not include markdown filtering (```json) in the response."
        )

    @staticmethod
    def create_grading_prompt(code_files: Dict[str, str], requirements: str) -> str:
        """Create the user prompt with code and requirements."""
        prompt = f"Requirements:\n{requirements}\n\nStudent Code:\n"
        for filename, content in code_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += "\nEvaluate this submission based on the requirements."
        return prompt


class ResponseParser:
    """Parses AI responses."""
    
    @staticmethod
    def parse_json_response(raw_response: str) -> dict[str, Any]:
        """Extract and parse JSON from response."""
        clean_response = raw_response.strip()
        # Handle markdown code blocks if present despite instructions
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
            
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}") from e

    @staticmethod
    def create_grading_result(data: dict[str, Any]) -> GradingResult:
        """Convert dictionary to GradingResult."""
        return GradingResult(
            score=data.get("score", 0),
            feedback=data.get("feedback", "No feedback provided."),
            suggestions=data.get("suggestions", []),
            confidence=data.get("confidence", 0.0)
        )


class GradingAssistant:
    """Coordinator for the grading process."""
    
    def __init__(self, client: AnthropicClient):
        self.client = client
        self.prompt_factory = PromptFactory()
        self.parser = ResponseParser()

    def grade_assignment(self, code_files: Dict[str, str], requirements: str) -> GradingResult:
        """
        Grade a student assignment.
        
        Args:
            code_files: Dict mapping filenames to content
            requirements: Assignment requirements text
        """
        system_prompt = self.prompt_factory.create_system_prompt()
        user_prompt = self.prompt_factory.create_grading_prompt(code_files, requirements)
        
        raw_response = self.client.analyze_code(system_prompt, user_prompt)
        parsed_data = self.parser.parse_json_response(raw_response)
        
        return self.parser.create_grading_result(parsed_data)
