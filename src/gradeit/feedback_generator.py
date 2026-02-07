"""
Feedback Generation module for GradeIt.
Generates Markdown reports from grading results.
"""

from pathlib import Path
from typing import Optional
from .student_loader import Student
from .gradle_runner import BuildResult
from .test_parser import ExecutionSummary
from .ai_grader import GradingResult


class MarkdownRenderer:
    """Renders grading components as Markdown."""
    
    @staticmethod
    def render_header(student: Student) -> str:
        """Render the report header."""
        return (
            f"# Grading Report: {student.username}\n"
            f"**Group**: {student.group_name}\n"
            f"**Semester**: {student.semester}\n"
            f"**Course**: {student.course} Section {student.section}\n"
            "---\n"
        )

    @staticmethod
    def render_build_status(build: BuildResult) -> str:
        """Render build status section."""
        status_icon = "✅" if build.success else "❌"
        return (
            f"## Build Status: {status_icon}\n"
            "```\n"
            f"{build.output[:1000]}...\n"  # Truncate long output
            "```\n"
            "---\n"
        )

    @staticmethod
    def render_test_results(summary: ExecutionSummary) -> str:
        """Render test results section."""
        score_percent = 0
        if summary.total > 0:
            score_percent = (summary.passed / summary.total) * 100
            
        return (
            f"## Test Results\n"
            f"- **Passed**: {summary.passed}/{summary.total}\n"
            f"- **Score**: {score_percent:.1f}%\n"
            f"- **Failures**: {len(summary.failures)}\n"
            "---\n"
        )

    @staticmethod
    def render_ai_feedback(result: GradingResult) -> str:
        """Render AI feedback section."""
        suggestions = "\n".join(f"- {s}" for s in result.suggestions)
        return (
            f"## AI Feedback\n"
            f"**AI Score**: {result.score}/100 (Confidence: {result.confidence})\n\n"
            f"### Analysis\n{result.feedback}\n\n"
            f"### Suggestions\n{suggestions}\n"
        )


class FeedbackGenerator:
    """Generates and saves feedback reports."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.renderer = MarkdownRenderer()

    def generate_report(
        self, 
        student: Student, 
        build: BuildResult, 
        tests: ExecutionSummary, 
        ai_result: GradingResult
    ) -> str:
        """Generate complete markdown report."""
        sections = [
            self.renderer.render_header(student),
            self.renderer.render_build_status(build),
            self.renderer.render_test_results(tests),
            self.renderer.render_ai_feedback(ai_result)
        ]
        return "\n".join(sections)

    def append_to_file(self, assignment: str, report: str) -> Path:
        """Append report to the assignment feedback file."""
        filename = f"{assignment}_Feedback.md"
        file_path = self.output_dir / filename
        
        mode = 'a' if file_path.exists() else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(report + "\n\n")
            
        return file_path
