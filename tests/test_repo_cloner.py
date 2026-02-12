"""
Unit tests for RepositoryCloner and helper classes.
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from git import GitCommandError
from src.gradeit.repo_cloner import RepositoryCloner, CloneResult, DirectoryManager, GitRunner
from src.gradeit.student_loader import Student


class TestDirectoryManager:
    """Tests for DirectoryManager helper."""
    
    def test_prepare_directory_exists_no_force(self, tmp_path):
        """Test preparation when dir exists and force is False."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        result = DirectoryManager.prepare_directory(repo_path, force=False)
        assert result is False
        assert repo_path.exists()
        
    def test_prepare_directory_exists_force(self, tmp_path):
        """Test preparation when dir exists and force is True."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "file.txt").touch()
        
        result = DirectoryManager.prepare_directory(repo_path, force=True)
        assert result is True
        assert not repo_path.exists() # Should be removed
        
    def test_create_student_dir(self, tmp_path):
        """Test student directory creation."""
        student_dir = DirectoryManager.create_student_dir(tmp_path, "user1")
        assert student_dir == tmp_path / "user1"
        assert student_dir.exists()


class TestGitRunner:
    """Tests for GitRunner helper."""
    
    @patch('src.gradeit.repo_cloner.Repo.clone_from')
    def test_clone(self, mock_clone, tmp_path):
        """Test git clone wrapper."""
        url = "git@test.com:repo.git"
        GitRunner.clone(url, tmp_path)
        mock_clone.assert_called_once_with(url, str(tmp_path))


class TestRepositoryCloner:
    """Test cases for RepositoryCloner class."""
    
    @pytest.fixture
    def cloner(self, tmp_path):
        return RepositoryCloner(str(tmp_path), "gitlab.hfcc.edu")
        
    @pytest.fixture
    def student(self):
        return Student.from_group_name("mawall-2026-winter-cis-271-01")

    @patch('src.gradeit.repo_cloner.GitRunner.clone')
    def test_clone_student_repo_success(self, mock_clone, cloner, student, tmp_path):
        """Test successful clone."""
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is True
        assert result.repo_path == tmp_path / "mawall" / "fizzbuzz"
        assert result.already_existed is False
        mock_clone.assert_called_once()
    
    @patch('src.gradeit.repo_cloner.GitRunner.clone')
    def test_clone_student_repo_failure(self, mock_clone, cloner, student):
        """Test failed clone."""
        mock_clone.side_effect = GitCommandError("clone", "Error")
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is False
        assert result.already_existed is False
        assert "Error" in result.error
        
    @patch('src.gradeit.repo_cloner.GitRunner.clone')
    def test_clone_student_repo_already_exists(self, mock_clone, cloner, student, tmp_path):
        """Test repo that already exists is skipped."""
        # Create the repo directory to simulate it already existing
        repo_path = tmp_path / "mawall" / "fizzbuzz"
        repo_path.mkdir(parents=True)
        
        result = cloner.clone_student_repo(student, "fizzbuzz")
        
        assert result.success is True
        assert result.already_existed is True
        assert result.repo_path == repo_path
        mock_clone.assert_not_called()  # Should not attempt to clone
    
    @patch('src.gradeit.repo_cloner.GitRunner.clone')
    def test_clone_all_repos(self, mock_clone, cloner, student):
        """Test cloning multiple repos."""
        results = cloner.clone_all_repos([student], "fizzbuzz")
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].already_existed is False

    def test_get_clone_summary(self, cloner, student):
        """Test summary generation."""
        results = [
            CloneResult(student, True),
            CloneResult(student, False)
        ]
        summary = cloner.get_clone_summary(results)
        assert summary['successful'] == 1
        assert summary['failed'] == 1
        assert summary['total'] == 2
