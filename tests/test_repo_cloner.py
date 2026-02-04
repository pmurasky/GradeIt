"""
Unit tests for RepositoryCloner
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from git import GitCommandError
from src.gradeit.repo_cloner import RepositoryCloner, CloneResult
from src.gradeit.student_loader import Student


class TestCloneResult:
    """Test cases for CloneResult class."""
    
    def test_clone_result_success(self):
        """Test successful clone result."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        result = CloneResult(
            student=student,
            success=True,
            repo_path=Path("/tmp/test"),
            error=None
        )
        
        assert result.success is True
        assert result.student == student
        assert result.repo_path == Path("/tmp/test")
        assert result.error is None
    
    def test_clone_result_failure(self):
        """Test failed clone result."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        result = CloneResult(
            student=student,
            success=False,
            repo_path=None,
            error="Repository not found"
        )
        
        assert result.success is False
        assert result.error == "Repository not found"
        assert result.repo_path is None
    
    def test_repr(self):
        """Test string representation."""
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        result = CloneResult(student=student, success=True)
        repr_str = repr(result)
        
        assert "CloneResult" in repr_str
        assert "mawall" in repr_str
        assert "SUCCESS" in repr_str


class TestRepositoryCloner:
    """Test cases for RepositoryCloner class."""
    
    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates base directory."""
        base_dir = tmp_path / "repos"
        cloner = RepositoryCloner(str(base_dir), "gitlab.hfcc.edu")
        
        assert base_dir.exists()
        assert cloner.base_directory == base_dir
        assert cloner.gitlab_host == "gitlab.hfcc.edu"
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_student_repo_success(self, mock_clone, tmp_path):
        """Test successful repository clone."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is True
        assert result.student == student
        assert result.repo_path == tmp_path / "mawall" / "fizzbuzz"
        assert result.error is None
        
        # Verify clone was called with correct URL
        expected_url = "git@gitlab.hfcc.edu:mawall-2026-winter-cis-271-01/fizzbuzz.git"
        mock_clone.assert_called_once()
        assert mock_clone.call_args[0][0] == expected_url
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_student_repo_already_exists(self, mock_clone, tmp_path):
        """Test cloning when repository already exists."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        # Create the directory to simulate existing repo
        repo_path = tmp_path / "mawall" / "fizzbuzz"
        repo_path.mkdir(parents=True)
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is True
        assert result.repo_path == repo_path
        
        # Clone should not be called since repo exists
        mock_clone.assert_not_called()
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_student_repo_force_reclone(self, mock_clone, tmp_path):
        """Test force re-clone when repository already exists."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        # Create the directory to simulate existing repo
        repo_path = tmp_path / "mawall" / "fizzbuzz"
        repo_path.mkdir(parents=True)
        (repo_path / "old_file.txt").write_text("old content")
        
        result = cloner.clone_student_repo(student, "fizzbuzz", force=True)
        
        assert result.success is True
        
        # Clone should be called even though repo existed
        mock_clone.assert_called_once()
        
        # Old file should be gone
        assert not (repo_path / "old_file.txt").exists()
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_student_repo_git_error(self, mock_clone, tmp_path):
        """Test handling of Git command errors."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        # Simulate Git error
        mock_clone.side_effect = GitCommandError("clone", "Repository not found")
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is False
        assert result.error is not None
        assert "Repository not found" in result.error
        assert result.repo_path is None
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_student_repo_unexpected_error(self, mock_clone, tmp_path):
        """Test handling of unexpected errors."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        student = Student.from_group_name("mawall-2026-winter-cis-271-01")
        
        # Simulate unexpected error
        mock_clone.side_effect = Exception("Unexpected error")
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is False
        assert "Unexpected error" in result.error
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_all_repos(self, mock_clone, tmp_path):
        """Test cloning multiple repositories."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        
        students = [
            Student.from_group_name("mawall-2026-winter-cis-271-01"),
            Student.from_group_name("jdoe-2026-winter-cis-271-01"),
            Student.from_group_name("asmith-2026-winter-cis-271-01"),
        ]
        
        results = cloner.clone_all_repos(students, "fizzbuzz")
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert mock_clone.call_count == 3
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone_all_repos_mixed_results(self, mock_clone, tmp_path):
        """Test cloning with some successes and some failures."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        
        students = [
            Student.from_group_name("mawall-2026-winter-cis-271-01"),
            Student.from_group_name("jdoe-2026-winter-cis-271-01"),
        ]
        
        # First clone succeeds, second fails
        mock_clone.side_effect = [
            None,  # Success
            GitCommandError("clone", "Repository not found")  # Failure
        ]
        
        results = cloner.clone_all_repos(students, "fizzbuzz")
        
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
    
    def test_get_clone_summary(self, tmp_path):
        """Test clone summary statistics."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        
        students = [
            Student.from_group_name("mawall-2026-winter-cis-271-01"),
            Student.from_group_name("jdoe-2026-winter-cis-271-01"),
            Student.from_group_name("asmith-2026-winter-cis-271-01"),
        ]
        
        results = [
            CloneResult(students[0], success=True),
            CloneResult(students[1], success=True),
            CloneResult(students[2], success=False, error="Failed"),
        ]
        
        summary = cloner.get_clone_summary(results)
        
        assert summary['total'] == 3
        assert summary['successful'] == 2
        assert summary['failed'] == 1
        assert summary['success_rate'] == pytest.approx(66.67, rel=0.1)
    
    def test_get_clone_summary_empty(self, tmp_path):
        """Test clone summary with no results."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        summary = cloner.get_clone_summary([])
        
        assert summary['total'] == 0
        assert summary['successful'] == 0
        assert summary['failed'] == 0
        assert summary['success_rate'] == 0
    
    def test_repr(self, tmp_path):
        """Test string representation."""
        cloner = RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        repr_str = repr(cloner)
        
        assert "RepositoryCloner" in repr_str
        assert str(tmp_path) in repr_str
        assert "gitlab.hfcc.edu" in repr_str
