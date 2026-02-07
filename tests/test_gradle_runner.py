"""
Tests for the GradleRunner class.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from gradeit.gradle_runner import GradleRunner, BuildResult


@pytest.fixture
def mock_subprocess():
    with patch('subprocess.run') as mock:
        yield mock


@pytest.fixture
def runner():
    return GradleRunner()


def test_run_build_success(runner, mock_subprocess, tmp_path):
    """Test successful build execution."""
    # Setup mock
    process_mock = MagicMock()
    process_mock.returncode = 0
    process_mock.stdout = "BUILD SUCCESSFUL"
    process_mock.stderr = ""
    mock_subprocess.return_value = process_mock
    
    # Create dummy project dir and wrapper
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / "gradlew").touch(mode=0o755)
    
    # Execute
    result = runner.run_build(project_dir)
    
    # Verify
    assert result.success is True
    assert "BUILD SUCCESSFUL" in result.output
    assert result.error is None
    mock_subprocess.assert_called_once()
    
    # Check command arguments
    args = mock_subprocess.call_args[0][0]
    assert str(project_dir / "gradlew") in args[0]
    assert "build" in args


def test_run_build_failure(runner, mock_subprocess, tmp_path):
    """Test failed build execution."""
    # Setup mock
    process_mock = MagicMock()
    process_mock.returncode = 1
    process_mock.stdout = "BUILD FAILED"
    process_mock.stderr = "Compilation error"
    mock_subprocess.return_value = process_mock
    
    # Create dummy project dir and wrapper
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / "gradlew").touch(mode=0o755)
    
    # Execute
    result = runner.run_build(project_dir)
    
    # Verify
    assert result.success is False
    assert "BUILD FAILED" in result.output
    assert "Compilation error" in result.output
    assert result.error is not None


def test_project_path_not_exist(runner):
    """Test handling of non-existent project path."""
    result = runner.run_build(Path("/non/existent/path"))
    
    assert result.success is False
    assert "does not exist" in result.error


def test_wrapper_not_found_fallback(mock_subprocess, tmp_path):
    """Test fallback to system gradle when wrapper is missing."""
    # Setup mock
    process_mock = MagicMock()
    process_mock.returncode = 0
    process_mock.stdout = "OK"
    process_mock.stderr = ""
    mock_subprocess.return_value = process_mock
    
    runner = GradleRunner(use_wrapper=True) # Even if True, should fallback if file missing
    
    # Create dummy project dir WITHOUT wrapper
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Execute
    result = runner.run_build(project_dir)
    
    # Verify called with 'gradle'
    args = mock_subprocess.call_args[0][0]
    assert args[0] == 'gradle'


def test_execution_exception(runner, mock_subprocess, tmp_path):
    """Test handling of subprocess exceptions."""
    # Setup mock to raise exception
    mock_subprocess.side_effect = Exception("System error")
    
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / "gradlew").touch(mode=0o755)
    
    result = runner.run_build(project_dir)
    
    assert result.success is False
    assert "System error" in result.error
