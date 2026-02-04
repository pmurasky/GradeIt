"""
Unit tests for StudentLoader
"""

import pytest
import tempfile
from pathlib import Path
from src.gradeit.student_loader import Student, StudentLoader


class TestStudent:
    """Test cases for Student class."""
    
    def test_from_group_name_standard_format(self):
        """Test parsing a standard group name."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        assert student.group_name == "mawall-2026-winter-cis-271-01"
        assert student.username == "mawall"
        assert student.semester == "2026-winter"
        assert student.course == "cis-271"
        assert student.section == "01"
    
    def test_from_group_name_with_capital_letters(self):
        """Test parsing group name with capital letters."""
        student = Student.from_group_name("SandovalJulio2026-winter-cis-271-01")
        
        # The parser looks for a standalone 4-digit year
        # Since "2026" is not standalone (no dash before "winter"), it treats
        # "SandovalJulio2026" as the username and falls back to default parsing
        assert student.username == "SandovalJulio2026"
        assert student.semester == "winter-cis"
    
    def test_from_group_name_with_mixed_case(self):
        """Test parsing group name with mixed case semester."""
        student = Student.from_group_name("Zmgarbie-2026-Winter-CIS-271-01")
        
        assert student.username == "Zmgarbie"
        assert student.semester == "2026-Winter"
        assert student.course == "CIS-271"
    
    def test_from_group_name_with_space_in_username(self):
        """Test parsing group name with space in username."""
        student = Student.from_group_name("Wessam Awad-2026-winter-cis-271-01")
        
        assert student.username == "Wessam Awad"
        assert student.semester == "2026-winter"
    
    def test_from_group_name_with_trailing_period(self):
        """Test parsing group name with trailing period."""
        student = Student.from_group_name("qmevans-2026-winter-cis-271-01.")
        
        assert student.group_name == "qmevans-2026-winter-cis-271-01."
        assert student.username == "qmevans"
    
    def test_from_group_name_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid group name format"):
            Student.from_group_name("invalid")
    
    def test_from_group_name_too_few_parts(self):
        """Test that too few parts raises ValueError."""
        with pytest.raises(ValueError, match="Invalid group name format"):
            Student.from_group_name("user-2026")
    
    def test_get_repo_url(self):
        """Test generating repository URL."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        url = student.get_repo_url("gitlab.hfcc.edu", "fizzbuzz")
        
        assert url == "git@gitlab.hfcc.edu:mawall-2026-winter-cis-271-01/fizzbuzz.git"
    
    def test_repr(self):
        """Test string representation."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        repr_str = repr(student)
        
        assert "Student" in repr_str
        assert "mawall" in repr_str


class TestStudentLoader:
    """Test cases for StudentLoader class."""
    
    def test_load_students_success(self, tmp_path):
        """Test loading students from a valid file."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("""
# Students for CIS 271
mawall-2026-winter-cis-271-01
SandovalJulio2026-winter-cis-271-01
Zmgarbie-2026-Winter-CIS-271-01
        """)
        
        loader = StudentLoader(str(students_file))
        students = loader.load_students()
        
        assert len(students) == 3
        assert students[0].username == "mawall"
        assert students[1].username == "SandovalJulio2026"
        assert students[2].username == "Zmgarbie"
    
    def test_load_students_with_trailing_periods(self, tmp_path):
        """Test loading students with trailing periods."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("""
mawall-2026-winter-cis-271-01.
qmevans-2026-winter-cis-271-01.
        """)
        
        loader = StudentLoader(str(students_file))
        students = loader.load_students()
        
        assert len(students) == 2
        assert students[0].username == "mawall"
        assert students[1].username == "qmevans"
    
    def test_load_students_empty_file(self, tmp_path):
        """Test loading from an empty file."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("")
        
        loader = StudentLoader(str(students_file))
        students = loader.load_students()
        
        assert len(students) == 0
    
    def test_load_students_only_comments(self, tmp_path):
        """Test loading from a file with only comments."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("""
# Comment 1
# Comment 2
        """)
        
        loader = StudentLoader(str(students_file))
        students = loader.load_students()
        
        assert len(students) == 0
    
    def test_load_students_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        loader = StudentLoader("/nonexistent/students.txt")
        
        with pytest.raises(FileNotFoundError):
            loader.load_students()
    
    def test_load_students_invalid_format(self, tmp_path):
        """Test that ValueError is raised for invalid student format."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("""
mawall-2026-winter-cis-271-01
invalid-format
        """)
        
        loader = StudentLoader(str(students_file))
        
        with pytest.raises(ValueError, match="Errors parsing students file"):
            loader.load_students()
    
    def test_load_students_mixed_valid_invalid(self, tmp_path):
        """Test that all errors are reported when multiple invalid entries exist."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("""
mawall-2026-winter-cis-271-01
invalid1
invalid2
        """)
        
        loader = StudentLoader(str(students_file))
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_students()
        
        error_msg = str(exc_info.value)
        assert "Line 3" in error_msg
        assert "Line 4" in error_msg
    
    def test_repr(self, tmp_path):
        """Test string representation."""
        students_file = tmp_path / "students.txt"
        students_file.write_text("")
        
        loader = StudentLoader(str(students_file))
        repr_str = repr(loader)
        
        assert "StudentLoader" in repr_str
        assert str(students_file) in repr_str
