"""
AI Grading components for GradeIt.
Handles interaction with Anthropic/Claude for code analysis.
"""

import json
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from .ai_clients import AIClient

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
    def create_grading_prompt(code_files: Dict[str, str], requirements: str, solution_files: Dict[str, str] = None, file_context: Dict[str, str] = None) -> str:
        """Create the user prompt with code and requirements."""
        prompt = f"Requirements:\n{requirements}\n"
        
        if file_context:
            prompt += "\nFile-Specific Instructions (from headers):\n"
            for filename, header in file_context.items():
                prompt += f"\n--- {filename} Instructions ---\n{header}\n"
            prompt += "\nUse the above instructions to verify the student implemented the specific requirements described in the file headers.\n"

        if solution_files:
            prompt += "\nReference Solution:\n"
            for filename, content in solution_files.items():
                prompt += f"\n--- {filename} (Solution) ---\n{content}\n"
            prompt += "\nCompare the student's work against this reference solution.\n"

        prompt += "\nStudent Code:\n"
        for filename, content in code_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += "\nEvaluate this submission based on the requirements and reference solution."
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
    
    def __init__(self, client: AIClient):
        self.client = client
        self.prompt_factory = PromptFactory()
        self.parser = ResponseParser()

    def grade_assignment(self, code_files: Dict[str, str], requirements: str, max_grade: int = 100, solution_files: Dict[str, str] = None, file_context: Dict[str, str] = None) -> GradingResult:
        """
        Grade a student assignment.
        """
        system_prompt = self.prompt_factory.create_system_prompt()
        user_prompt = self.prompt_factory.create_grading_prompt(code_files, requirements, solution_files, file_context)
        
        # Combine prompts as generic clients take a single prompt or handle context internally
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        raw_response = self.client.analyze_code(full_prompt)
        try:
            parsed_data = self.parser.parse_json_response(raw_response)
        except ValueError as e:
            # Fallback/Debug: print raw response to help user identify the issue
            print(f"\n[DEBUG] AI Raw Response:\n{raw_response}\n[END DEBUG]")
            raise e
            
        result = self.parser.create_grading_result(parsed_data)
        
        # Scale score if max_grade is not 100
        if max_grade != 100:
            result.score = int((result.score / 100.0) * max_grade)
            
        return result
