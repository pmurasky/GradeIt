"""
Student data loader for GradeIt.
Reads and parses student information from students.txt file.
"""

from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


class StudentNameParser:
    """Parses student group names into components."""
    
    @staticmethod
    def parse(group_name: str) -> Tuple[str, str, str, str]:
        """
        Parse a group name into (username, semester, course, section).
        
        Args:
            group_name: Full GitLab group name
            
        Returns:
            Tuple of (username, semester, course, section)
            
        Raises:
            ValueError: If format is invalid
        """
        parts = group_name.strip().split('-')
        if len(parts) < 4:
            raise ValueError(f"Invalid group name format: '{group_name}'")
            
        username_parts, remaining = StudentNameParser._extract_username(parts)
        if not username_parts:
             # Fallback: assume first part is username
            username_parts = [parts[0]]
            remaining = parts[1:]
            
        username = '-'.join(username_parts)
        
        semester, course, section = StudentNameParser._parse_remaining(remaining)
        
        return username, semester, course, section

    @staticmethod
    def _extract_username(parts: List[str]) -> Tuple[List[str], List[str]]:
        """Extract username components based on year position."""
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4:
                return parts[:i], parts[i:]
        return [], parts

    @staticmethod
    def _parse_remaining(parts: List[str]) -> Tuple[str, str, str]:
        """Parse semester, course, and section from remaining parts."""
        if len(parts) >= 5:
            # year, sem_name, course_name, course_num, section
            year, sem, c_name, c_num, sect = parts[0], parts[1], parts[2], parts[3], parts[4]
            return f"{year}-{sem}", f"{c_name}-{c_num}", sect
            
        if len(parts) == 4:
            # year, sem_name, course, section
            year, sem, course, sect = parts[0], parts[1], parts[2], parts[3]
            return f"{year}-{sem}", course, sect
            
        raise ValueError("Could not parse semester/course/section information.")


@dataclass
class Student:
    """Represents a student with their GitLab group information."""
    
    group_name: str
    username: str
    semester: str
    course: str
    section: str
    
    @classmethod
    def from_group_name(cls, group_name: str) -> 'Student':
        """Create a Student from a group name."""
        try:
            user, sem, course, section = StudentNameParser.parse(group_name)
            return cls(
                group_name=group_name.strip(),
                username=user,
                semester=sem,
                course=course,
                section=section
            )
        except ValueError as e:
            # Re-raise with original context if needed, or just let it bubble
            # Adding context for clarity if it was a generic error
            if "Invalid group name" not in str(e):
                 raise ValueError(f"Invalid group name format: '{group_name}'") from e
            raise

    def get_repo_url(self, gitlab_host: str, assignment: str) -> str:
        """Get the GitLab repository URL."""
        return f"git@{gitlab_host}:{self.group_name}/{assignment}.git"
    
    def __repr__(self) -> str:
        return f"Student(username='{self.username}', group='{self.group_name}')"


class StudentLoader:
    """Loads student data from students.txt file."""
    
    def __init__(self, students_file: str):
        self.students_file = Path(students_file)
    
    def load_students(self) -> List[Student]:
        """Load all students from the students.txt file."""
        if not self.students_file.exists():
            raise FileNotFoundError(f"Students file not found: {self.students_file}")
        
        students = []
        errors = []
        
        with open(self.students_file, 'r') as f:
            for line_num, line in enumerate(f, start=1):
                if student := self._parse_line(line, line_num, errors):
                    students.append(student)
        
        if errors:
            raise ValueError("Errors parsing students file:\n" + "\n".join(errors))
        
        return students

    def _parse_line(self, line: str, line_num: int, errors: List[str]) -> Student | None:
        """Parse a single line from the file."""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
            
        line = line.rstrip('.')
        try:
            return Student.from_group_name(line)
        except ValueError as e:
            errors.append(f"Line {line_num}: {e}")
            return None
    
    def __repr__(self) -> str:
        return f"StudentLoader(file='{self.students_file}')"
