"""
GitLab repository cloner for GradeIt.
Handles cloning student repositories via SSH.
"""

import shutil
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from git import Repo, GitCommandError
from .student_loader import Student


@dataclass
class CloneResult:
    """Result of a repository clone operation."""
    student: Student
    success: bool
    repo_path: Optional[Path] = None
    error: Optional[str] = None
    
    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"CloneResult({self.student.username}: {status})"


class DirectoryManager:
    """Handles directory creation and cleanup."""
    
    @staticmethod
    def prepare_directory(path: Path, force: bool) -> bool:
        """
        Prepare directory for cloning.
        Returns True if clone should proceed, False if already exists and valid.
        """
        if path.exists():
            if force:
                shutil.rmtree(path)
                return True
            return False
        return True

    @staticmethod
    def create_student_dir(base_dir: Path, username: str) -> Path:
        """Create and return student directory."""
        student_dir = base_dir / username
        student_dir.mkdir(parents=True, exist_ok=True)
        return student_dir

    @staticmethod
    def cleanup_on_failure(path: Path):
        """Clean up failed clone directory."""
        if path.exists():
            shutil.rmtree(path)


class GitRunner:
    """Executes Git operations."""
    
    @staticmethod
    def clone(url: str, path: Path) -> None:
        """Clone repository from URL to path."""
        Repo.clone_from(url, str(path))


class RepositoryCloner:
    """Clones student repositories from GitLab."""
    
    def __init__(self, base_directory: str, gitlab_host: str):
        self.base_directory = Path(base_directory)
        self.gitlab_host = gitlab_host
        self.base_directory.mkdir(parents=True, exist_ok=True)
    
    def clone_student_repo(self, student: Student, assignment: str, force: bool = False) -> CloneResult:
        """Clone a single student's repository."""
        student_dir = DirectoryManager.create_student_dir(
            self.base_directory, student.username
        )
        repo_path = student_dir / assignment
        
        if not DirectoryManager.prepare_directory(repo_path, force):
            return CloneResult(student, True, repo_path)
        
        return self._perform_clone(student, assignment, repo_path)

    def _perform_clone(self, student: Student, assignment: str, path: Path) -> CloneResult:
        """Execute the clone operation and handle errors."""
        repo_url = student.get_repo_url(self.gitlab_host, assignment)
        try:
            GitRunner.clone(repo_url, path)
            return CloneResult(student, True, path)
        except (GitCommandError, Exception) as e:
            DirectoryManager.cleanup_on_failure(path)
            return CloneResult(student, False, None, str(e))
    
    def clone_all_repos(self, students: List[Student], assignment: str, force: bool = False) -> List[CloneResult]:
        """Clone repositories for all students."""
        return [
            self.clone_student_repo(student, assignment, force)
            for student in students
        ]
    
    def get_clone_summary(self, results: List[CloneResult]) -> dict:
        """Get a summary of clone results."""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        return {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
    
    def __repr__(self) -> str:
        return f"RepositoryCloner(base_dir='{self.base_directory}', host='{self.gitlab_host}')"
