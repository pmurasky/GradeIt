"""
Unit tests for Feedback Generation module.
"""

import pytest
from pathlib import Path
from src.gradeit.student_loader import Student
from src.gradeit.gradle_runner import BuildResult
from src.gradeit.test_parser import ExecutionSummary
from src.gradeit.ai_grader import GradingResult
from src.gradeit.feedback_generator import MarkdownRenderer, FeedbackGenerator


@pytest.fixture
def sample_data():
    student = Student("group", "user", "2024", "cis", "01")
    build = BuildResult(True, "Build Success")
    tests = ExecutionSummary(10, 8, 2, 0)
    ai = GradingResult(
        score=90, 
        feedback="Good code", 
        suggestions=["Fix indent"], 
        confidence=0.9
    )
    return student, build, tests, ai


class TestMarkdownRenderer:
    """Tests for MarkdownRenderer."""

    def test_render_header(self, sample_data):
        student = sample_data[0]
        output = MarkdownRenderer.render_header(student)
        assert f"# Grading Report: {student.username}" in output
        assert f"**Group**: {student.group_name}" in output

    def test_render_build_status(self, sample_data):
        build = sample_data[1]
        output = MarkdownRenderer.render_build_status(build)
        assert "## Build Status: ✅" in output
        assert "Build Success" in output

    def test_render_test_results(self, sample_data):
        tests = sample_data[2]
        output = MarkdownRenderer.render_test_results(tests)
        assert "## Test Results" in output
        assert "Passed**: 8/10" in output
        assert "Score**: 80.0%" in output

    def test_render_ai_feedback(self, sample_data):
        ai = sample_data[3]
        output = MarkdownRenderer.render_ai_feedback(ai)
        assert "## AI Feedback" in output
        assert "AI Score**: 90/100" in output
        assert "- Fix indent" in output


class TestFeedbackGenerator:
    """Tests for FeedbackGenerator."""

    def test_generate_report(self, tmp_path, sample_data):
        generator = FeedbackGenerator(str(tmp_path))
        student, build, tests, ai = sample_data
        
        report = generator.generate_report(student, build, tests, ai)
        
        assert "# Grading Report" in report
        assert "## Build Status" in report
        assert "## Test Results" in report
        assert "## AI Feedback" in report

    def test_append_to_file(self, tmp_path, sample_data):
        generator = FeedbackGenerator(str(tmp_path))
        report_content = "# Report Content"
        
        # First write (should resolve to base name)
        path = generator.append_to_file("assign1", report_content)
        assert path.exists()
        assert path.name == "assign1_Feedback.md"
        assert report_content in path.read_text()
        
        # Second write (append to SAME file because it's cached in generator instance)
        generator.append_to_file("assign1", "Second Report")
        content = path.read_text()
        assert "Second Report" in content
        assert content.count("# Report Content") == 1

    def test_versioning_new_file(self, tmp_path):
        """Test that a new generator instance respects existing files."""
        # Create a pre-existing file
        (tmp_path / "assign2_Feedback.md").write_text("Old Run")
        
        # New run/generator instance
        generator = FeedbackGenerator(str(tmp_path))
        path = generator.append_to_file("assign2", "New Run")
        
        # Should create version 1
        assert path.name == "assign2_Feedback_1.md"
        assert path.read_text().strip() == "New Run"
        
        # Original should be untouched
        assert (tmp_path / "assign2_Feedback.md").read_text() == "Old Run"
