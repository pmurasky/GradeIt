"""
Unit tests for CLI module.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from src.gradeit.cli import GradingManager, GradingContext, CloneResult
from src.gradeit.student_loader import Student


@pytest.fixture
def mock_ctx():
    ctx = MagicMock(spec=GradingContext)
    ctx.base_directory = "/tmp/repos"
    ctx.gitlab_host = "gitlab.example.com"
    ctx.assignment = "test-assign"
    return ctx


@pytest.fixture
def sample_students():
    return [
        Student("group1", "user1", "2024", "cis", "01"),
        Student("group2", "user2", "2024", "cis", "01")
    ]


class TestGradingManager:
    """Tests for GradingManager."""

    @patch('src.gradeit.cli.RepositoryCloner')
    @patch('src.gradeit.cli.tqdm')
    def test_clone_repos(self, mock_tqdm, mock_cloner_cls, mock_ctx, sample_students):
        """Test cloning with progress bar."""
        # Setup mocks
        mock_cloner = mock_cloner_cls.return_value
        mock_cloner.clone_student_repo.return_value = CloneResult(sample_students[0], True)
        
        # Mock tqdm context manager
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar
        
        # Execute
        results = GradingManager.clone_repos(mock_ctx, sample_students)
        
        # Verify
        assert len(results) == 2
        assert mock_cloner.clone_student_repo.call_count == 2
        assert mock_pbar.update.call_count == 2
        mock_tqdm.assert_called_once()

    @patch('src.gradeit.cli.GradingPipeline')
    @patch('src.gradeit.cli.tqdm')
    def test_run_grading(self, mock_tqdm, mock_pipeline_cls, mock_ctx, sample_students):
        """Test grading with progress bar."""
        # Setup mocks
        mock_pipeline = mock_pipeline_cls.return_value
        
        results = [
            CloneResult(sample_students[0], True, Mock(exists=True)),
            CloneResult(sample_students[1], True, Mock(exists=True))
        ]
        
        # Mock tqdm context manager
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar
        
        # Execute
        GradingManager.run_grading(mock_ctx, results)
        
        # Verify
        assert mock_pipeline.process_student.call_count == 2
        assert mock_pbar.update.call_count == 2
        mock_tqdm.assert_called_once()

    @patch('src.gradeit.cli.GradingPipeline')
    def test_run_grading_no_repos(self, mock_pipeline_cls, mock_ctx):
        """Test grading with no successful clones."""
        GradingManager.run_grading(mock_ctx, [])
        mock_pipeline_cls.assert_not_called()
