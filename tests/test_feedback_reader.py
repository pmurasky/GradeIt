"""
Unit tests for FeedbackReader module.
"""

import pytest
from pathlib import Path
from src.gradeit.feedback_reader import FeedbackReader, FeedbackEntry


class TestFeedbackReader:
    """Test cases for FeedbackReader class."""
    
    @pytest.fixture
    def sample_feedback_single(self, tmp_path):
        """Create a sample feedback file with one student."""
        feedback_file = tmp_path / "test_feedback.md"
        content = """# Grading Report: jdoe
**Group**: jdoe-2026-winter-cis-271-01
**Semester**: 2026-winter
**Course**: cis-271 Section 01
---
## Build Status: ✅
```
BUILD SUCCESSFUL
```
---
## Test Results
- **Passed**: 10/10
- **Score**: 100.0%
- **Failures**: 0
---
## AI Feedback
**AI Score**: 95/100 (Confidence: 0.95)

### Analysis
Excellent work! Code is well-structured.

### Suggestions
- Consider adding more comments

"""
        feedback_file.write_text(content, encoding='utf-8')
        return feedback_file
    
    @pytest.fixture
    def sample_feedback_multiple(self, tmp_path):
        """Create a sample feedback file with multiple students."""
        feedback_file = tmp_path / "test_feedback.md"
        content = """# Grading Report: alice
**Group**: alice-2026-winter-cis-271-01
**Semester**: 2026-winter
**Course**: cis-271 Section 01
---
## Build Status: ✅
```
BUILD SUCCESSFUL
```
---
## AI Feedback
**AI Score**: 85/100 (Confidence: 0.90)

### Analysis
Good work overall.


# Grading Report: bob
**Group**: bob-2026-winter-cis-271-01
**Semester**: 2026-winter
**Course**: cis-271 Section 01
---
## Build Status: ❌
```
BUILD FAILED
```
---
## AI Feedback
**AI Score**: 60/100 (Confidence: 0.85)

### Analysis
Some improvements needed.

"""
        feedback_file.write_text(content, encoding='utf-8')
        return feedback_file
    
    @pytest.fixture
    def sample_feedback_missing_repo(self, tmp_path):
        """Create feedback with 'Repository not found' message."""
        feedback_file = tmp_path / "test_feedback.md"
        content = """# Grading Report: charlie
**Group**: charlie-2026-winter-cis-271-01
**Semester**: 2026-winter
**Course**: cis-271 Section 01
---
## Build Status: ❌
```
Repository not found. No build attempted.
```
---
## Test Results
- **Passed**: 0/0
- **Score**: 0.0%
- **Failures**: 0
---
## AI Feedback
**AI Score**: 0/100 (Confidence: 1.0)

### Analysis
**Homework not Completed**

The repository could not be found. Grade set to 0.

### Suggestions
- Ensure repository exists.
- Check naming conventions.

"""
        feedback_file.write_text(content, encoding='utf-8')
        return feedback_file
    
    def test_parse_empty_feedback_file(self, tmp_path):
        """Test parsing an empty feedback file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("", encoding='utf-8')
        
        reader = FeedbackReader()
        entries = reader.read_feedback_file(empty_file)
        
        assert entries == []
    
    def test_parse_single_student_feedback(self, sample_feedback_single):
        """Test parsing a feedback file with one student."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_single)
        
        assert len(entries) == 1
        assert entries[0].username == "jdoe"
        assert entries[0].has_grade is True
        assert entries[0].is_missing_repo is False
        assert "Excellent work!" in entries[0].raw_content
    
    def test_parse_multiple_student_feedback(self, sample_feedback_multiple):
        """Test parsing a feedback file with multiple students."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_multiple)
        
        assert len(entries) == 2
        assert entries[0].username == "alice"
        assert entries[1].username == "bob"
        assert all(entry.has_grade for entry in entries)
    
    def test_identify_missing_repo_feedback(self, sample_feedback_missing_repo):
        """Test detection of 'Repository not found' feedback."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_missing_repo)
        
        assert len(entries) == 1
        assert entries[0].username == "charlie"
        assert entries[0].is_missing_repo is True
        assert entries[0].has_grade is True  # Has a grade (0)
    
    def test_identify_normal_feedback(self, sample_feedback_single):
        """Test that normal feedback is not flagged as missing repo."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_single)
        
        assert entries[0].is_missing_repo is False
    
    def test_find_student_in_feedback(self, sample_feedback_multiple):
        """Test finding a specific student in parsed feedback."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_multiple)
        
        found = reader.find_student_feedback("alice", entries)
        
        assert found is not None
        assert found.username == "alice"
    
    def test_find_nonexistent_student(self, sample_feedback_multiple):
        """Test searching for a student that doesn't exist."""
        reader = FeedbackReader()
        entries = reader.read_feedback_file(sample_feedback_multiple)
        
        found = reader.find_student_feedback("nonexistent", entries)
        
        assert found is None
    
    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a file that doesn't exist."""
        nonexistent_file = tmp_path / "doesnt_exist.md"
        
        reader = FeedbackReader()
        entries = reader.read_feedback_file(nonexistent_file)
        
        assert entries == []
