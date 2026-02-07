"""
Unit tests for CLI module.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from click.testing import CliRunner
from src.gradeit.cli import cli, GradingManager, GradingContext, CloneResult

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_ctx():
    ctx = MagicMock(spec=GradingContext)
    ctx.base_directory = "/tmp/repos"
    ctx.gitlab_host = "gitlab.example.com"
    ctx.assignment = "test-assign"
    ctx.verbose = False
    return ctx

@pytest.fixture
def sample_students():
    from src.gradeit.student_loader import Student
    return [
        Student("group1", "user1", "2024", "cis", "01"),
        Student("group2", "user2", "2024", "cis", "01")
    ]

@patch('src.gradeit.cli.GradingManager')
@patch('src.gradeit.cli.ConfigLoader')
def test_clone_command(mock_config_cls, mock_manager, runner):
    """Test the clone subcommand."""
    # Setup
    mock_manager.load_students.return_value = []
    
    # Execute
    result = runner.invoke(cli, ['clone', '--assignment', 'test-assign'])
    
    # Verify
    assert result.exit_code == 0
    mock_manager.load_students.assert_called_once()
    mock_manager.clone_repos.assert_called_once()

@patch('src.gradeit.cli.GradingManager')
@patch('src.gradeit.cli.ConfigLoader')
def test_grade_command(mock_config_cls, mock_manager, runner, tmp_path):
    """Test the grade subcommand."""
    # Setup
    mock_manager.load_students.return_value = []
    
    # Setup config to return tmp_path as solutions_directory
    mock_config_instance = mock_config_cls.return_value
    mock_config_instance.get.side_effect = lambda k, d=None: str(tmp_path) if k == 'solutions_directory' else d

    # Create the solution folder inside the "solutions_directory" (tmp_path)
    sol_name = "MySolution"
    sol_dir = tmp_path / sol_name
    sol_dir.mkdir()
    
    # Execute with just the name
    result = runner.invoke(cli, ['grade', '--assignment', 'test-assign', '--solution', sol_name])
    
    # Verify
    assert result.exit_code == 0
    mock_manager.load_students.assert_called_once()
    mock_manager.run_grading.assert_called_once()

@patch('src.gradeit.cli.GradingManager')
@patch('src.gradeit.cli.ConfigLoader')
def test_missing_args(mock_config_cls, mock_manager, runner):
    """Test missing arguments."""
    result = runner.invoke(cli, ['clone']) # Missing assignment
    assert result.exit_code != 0
    assert "Missing option" in result.output

class TestGradingManagerLogic:
    """Tests for GradingManager logic (independent of Click)."""

    @patch('src.gradeit.cli.RepositoryCloner')
    @patch('src.gradeit.cli.tqdm')
    def test_clone_repos_logic(self, mock_tqdm, mock_cloner_cls, mock_ctx, sample_students):
        """Test cloning logic."""
        mock_ctx.assignment = "test-assign"
        mock_cloner = mock_cloner_cls.return_value
        mock_cloner.clone_student_repo.return_value = CloneResult(sample_students[0], True)
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar
        
        GradingManager.clone_repos(mock_ctx, sample_students)
        
        assert mock_cloner.clone_student_repo.call_count == 2

    @patch('src.gradeit.cli.FeedbackGenerator')
    @patch('src.gradeit.cli.GradingPipeline')
    @patch('src.gradeit.cli.tqdm')
    def test_run_grading_logic(self, mock_tqdm, mock_pipeline_cls, mock_feedback_cls, mock_ctx, sample_students):
        """Test grading logic."""
        mock_ctx.assignment = "test-assign"
        # Use MagicMock for path operations (support / operator)
        mock_ctx.base_directory = MagicMock()
        mock_ctx.repositories_directory = MagicMock()
        
        # Setup paths: first student exists, second does not
        repo_path_1 = MagicMock()
        repo_path_1.exists.return_value = True
        repo_path_2 = MagicMock()
        repo_path_2.exists.return_value = False
        
        # When accessing repositories_directory / username / assignment
        mock_ctx.repositories_directory.__truediv__.return_value.__truediv__.side_effect = [repo_path_1, repo_path_2]

        mock_pipeline = mock_pipeline_cls.return_value
        # Mock feedback generator attached to pipeline (created inside pipeline)
        # Note: In reality pipeline creates its own FeedbackGenerator. 
        # But we can verify pipeline calls if we mock the class used inside it.
        # Actually pipeline.process_student calls feedback.append_to_file.
        # But process_student is mocked here (mock_pipeline.process_student).
        
        # So we just need to verification that GradingManager logic calls pipeline correctly.
        # The logic flow is: GradingManager -> pipeline.process_student OR pipeline.process_missing_submission
        
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar
        
        # Execute
        GradingManager.run_grading(mock_ctx, sample_students)
        
        # Verify
        assert mock_pipeline.process_student.call_count == 1 # Only one exists
        assert mock_pipeline.process_missing_submission.call_count == 1 # One missing
