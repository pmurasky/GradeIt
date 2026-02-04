"""
Student data loader for GradeIt.
Reads and parses student information from students.txt file.
"""

from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class Student:
    """Represents a student with their GitLab group information."""
    
    group_name: str  # Full group name (e.g., mawall-2026-winter-cis-271-01)
    username: str    # Extracted username (e.g., mawall)
    semester: str    # Semester (e.g., 2026-winter)
    course: str      # Course (e.g., cis-271)
    section: str     # Section (e.g., 01)
    
    @classmethod
    def from_group_name(cls, group_name: str) -> 'Student':
        """
        Create a Student from a group name.
        
        Expected format: <username>-<year>-<semester>-<course>-<coursenumber>-<section>
        Example: mawall-2026-winter-cis-271-01
        
        Args:
            group_name: Full GitLab group name
            
        Returns:
            Student object
            
        Raises:
            ValueError: If group name format is invalid
        """
        parts = group_name.strip().split('-')
        
        if len(parts) < 5:
            raise ValueError(
                f"Invalid group name format: '{group_name}'. "
                f"Expected format: <username>-<year>-<semester>-<course>-<section>"
            )
        
        # Handle usernames that might contain spaces or special characters
        # The format is: username-year-semester-course-coursenumber-section
        # We need to find where the year starts (4 digits)
        username_parts = []
        remaining_parts = parts.copy()
        
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4:
                # Found the year, everything before is username
                username_parts = parts[:i]
                remaining_parts = parts[i:]
                break
        
        if not username_parts:
            # Fallback: assume first part is username
            username_parts = [parts[0]]
            remaining_parts = parts[1:]
        
        username = '-'.join(username_parts)
        
        # Parse remaining parts: year-semester-course-coursenumber-section
        # The course is typically: cis-271, so we need at least 5 parts
        if len(remaining_parts) >= 5:
            year = remaining_parts[0]
            semester_name = remaining_parts[1]
            course_name = remaining_parts[2]
            course_number = remaining_parts[3]
            section = remaining_parts[4]
            
            semester = f"{year}-{semester_name}"
            course = f"{course_name}-{course_number}"
        elif len(remaining_parts) == 4:
            # Handle case where course doesn't have a number (unlikely but possible)
            year = remaining_parts[0]
            semester_name = remaining_parts[1]
            course = remaining_parts[2]
            section = remaining_parts[3]
            
            semester = f"{year}-{semester_name}"
        else:
            raise ValueError(
                f"Invalid group name format: '{group_name}'. "
                f"Could not parse semester/course/section information."
            )
        
        return cls(
            group_name=group_name.strip(),
            username=username,
            semester=semester,
            course=course,
            section=section
        )
    
    def get_repo_url(self, gitlab_host: str, assignment: str) -> str:
        """
        Get the GitLab repository URL for this student's assignment.
        
        Args:
            gitlab_host: GitLab server hostname (e.g., gitlab.hfcc.edu)
            assignment: Assignment name (e.g., fizzbuzz)
            
        Returns:
            SSH URL for the repository
        """
        return f"git@{gitlab_host}:{self.group_name}/{assignment}.git"
    
    def __repr__(self) -> str:
        """String representation of the student."""
        return f"Student(username='{self.username}', group='{self.group_name}')"


class StudentLoader:
    """Loads student data from students.txt file."""
    
    def __init__(self, students_file: str):
        """
        Initialize the student loader.
        
        Args:
            students_file: Path to the students.txt file
        """
        self.students_file = Path(students_file)
    
    def load_students(self) -> List[Student]:
        """
        Load all students from the students.txt file.
        
        Returns:
            List of Student objects
            
        Raises:
            FileNotFoundError: If students.txt doesn't exist
            ValueError: If any student group name is invalid
        """
        if not self.students_file.exists():
            raise FileNotFoundError(f"Students file not found: {self.students_file}")
        
        students = []
        errors = []
        
        with open(self.students_file, 'r') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Remove trailing periods or other punctuation
                line = line.rstrip('.')
                
                try:
                    student = Student.from_group_name(line)
                    students.append(student)
                except ValueError as e:
                    errors.append(f"Line {line_num}: {e}")
        
        if errors:
            error_msg = "Errors parsing students file:\n" + "\n".join(errors)
            raise ValueError(error_msg)
        
        return students
    
    def __repr__(self) -> str:
        """String representation of the loader."""
        return f"StudentLoader(file='{self.students_file}')"
