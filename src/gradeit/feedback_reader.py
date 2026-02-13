"""
Feedback Reader module for GradeIt.
Reads and parses existing feedback files to determine grading status.
"""

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class FeedbackEntry:
    """Represents a parsed feedback entry for a student."""
    username: str
    has_grade: bool
    is_missing_repo: bool
    raw_content: str
    
    def __repr__(self) -> str:
        status = "missing_repo" if self.is_missing_repo else "graded"
        return f"FeedbackEntry({self.username}: {status})"


class FeedbackReader:
    """Reads and parses student feedback files."""
    
    # Pattern to identify student report headers
    REPORT_HEADER_PATTERN = r'^# Grading Report: (.+)$'
    
    # Patterns to identify missing repository feedback
    MISSING_REPO_INDICATORS = [
        "Repository not found",
        "Homework not Completed"
    ]
    
    @staticmethod
    def read_feedback_file(file_path: Path) -> List[FeedbackEntry]:
        """
        Read and parse a feedback file into individual student entries.
        
        Args:
            file_path: Path to the feedback markdown file
            
        Returns:
            List of FeedbackEntry objects, one per student
        """
        if not file_path.exists():
            return []
            
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return []
        
        if not content.strip():
            return []
        
        return FeedbackReader._parse_feedback_content(content)
    
    @staticmethod
    def _parse_feedback_content(content: str) -> List[FeedbackEntry]:
        """Parse feedback content into individual student entries."""
        entries = []
        lines = content.split('\n')
        
        current_username = None
        current_content = []
        
        for line in lines:
            # Check if this is a new student report header
            match = re.match(FeedbackReader.REPORT_HEADER_PATTERN, line)
            if match:
                # Save previous student's entry if exists
                if current_username:
                    entry = FeedbackReader._create_entry(
                        current_username, 
                        '\n'.join(current_content)
                    )
                    entries.append(entry)
                
                # Start new student
                current_username = match.group(1).strip()
                current_content = [line]
            else:
                # Add to current student's content
                if current_username:
                    current_content.append(line)
        
        # Don't forget the last student
        if current_username:
            entry = FeedbackReader._create_entry(
                current_username,
                '\n'.join(current_content)
            )
            entries.append(entry)
        
        return entries
    
    @staticmethod
    def _create_entry(username: str, content: str) -> FeedbackEntry:
        """Create a FeedbackEntry from username and content."""
        has_grade = True  # If feedback exists, they have some grade
        is_missing_repo = FeedbackReader._is_missing_repo_feedback(content)
        
        return FeedbackEntry(
            username=username,
            has_grade=has_grade,
            is_missing_repo=is_missing_repo,
            raw_content=content
        )
    
    @staticmethod
    def _is_missing_repo_feedback(content: str) -> bool:
        """
        Check if feedback indicates a missing repository.
        
        Args:
            content: The feedback content to check
            
        Returns:
            True if feedback contains missing repo indicators
        """
        return any(
            indicator in content 
            for indicator in FeedbackReader.MISSING_REPO_INDICATORS
        )
    
    @staticmethod
    def find_student_feedback(
        username: str, 
        entries: List[FeedbackEntry]
    ) -> Optional[FeedbackEntry]:
        """
        Find feedback entry for a specific student.
        
        Args:
            username: Student username to search for
            entries: List of parsed feedback entries
            
        Returns:
            FeedbackEntry if found, None otherwise
        """
        for entry in entries:
            if entry.username == username:
                return entry
        return None
