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
        self._resolved_paths = {}

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

    def _get_unique_path(self, assignment: str) -> Path:
        """Resolve a unique file path, handling version collision."""
        if assignment in self._resolved_paths:
            return self._resolved_paths[assignment]
            
        base_name = f"{assignment}_Feedback"
        filename = f"{base_name}.md"
        file_path = self.output_dir / filename
        
        counter = 1
        while file_path.exists():
            filename = f"{base_name}_{counter}.md"
            file_path = self.output_dir / filename
            counter += 1
            
        self._resolved_paths[assignment] = file_path
        return file_path

    def append_to_file(self, assignment: str, report: str) -> Path:
        """Append report to the assignment feedback file."""
        file_path = self._get_unique_path(assignment)
        
        mode = 'a' if file_path.exists() else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(report + "\n\n")
            
        return file_path

    def replace_student_feedback(self, assignment: str, username: str, new_report: str) -> Path:
        """
        Replace a specific student's feedback in the feedback file.
        
        Args:
            assignment: Assignment name
            username: Student username whose feedback to replace
            new_report: New report content to replace with
            
        Returns:
            Path to the updated feedback file
        """
        file_path = self._get_unique_path(assignment)
        
        if not file_path.exists():
            # If file doesn't exist, just append
            return self.append_to_file(assignment, new_report)
        
        # Read entire file
        content = file_path.read_text(encoding='utf-8')
        
        # Parse into individual student sections
        updated_content = self._replace_student_section(content, username, new_report)
        
        # Write back
        file_path.write_text(updated_content, encoding='utf-8')
        
        return file_path
    
    def _replace_student_section(self, content: str, username: str, new_report: str) -> str:
        """Replace a student's section in the feedback content."""
        import re
        
        # Pattern to match student report header
        pattern = rf'^# Grading Report: {re.escape(username)}$'
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        found = False
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is the start of the target student's section
            if re.match(pattern, line):
                found = True
                # Skip all lines until the next student report or end of file
                i += 1
                while i < len(lines):
                    # Check if we've hit the next student's report
                    if re.match(r'^# Grading Report: ', lines[i]):
                        break
                    i += 1
                
                # Insert the new report
                result_lines.append(new_report.rstrip())
                result_lines.append('')  # Blank line separator
                result_lines.append('')
                # Don't increment i, we want to process the next student's header
            else:
                result_lines.append(line)
                i += 1
        
        # If student wasn't found, append at the end
        if not found:
            if result_lines and result_lines[-1].strip():
                result_lines.append('')
            result_lines.append(new_report.rstrip())
            result_lines.append('')
        
        return '\n'.join(result_lines)

