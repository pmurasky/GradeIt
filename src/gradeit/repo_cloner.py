"""
GitLab repository cloner for GradeIt.
Handles cloning student repositories via SSH.
"""

import os
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
        """String representation of the clone result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"CloneResult({self.student.username}: {status})"


class RepositoryCloner:
    """Clones student repositories from GitLab."""
    
    def __init__(self, base_directory: str, gitlab_host: str):
        """
        Initialize the repository cloner.
        
        Args:
            base_directory: Base directory where repos will be cloned
            gitlab_host: GitLab server hostname (e.g., gitlab.hfcc.edu)
        """
        self.base_directory = Path(base_directory)
        self.gitlab_host = gitlab_host
        
        # Create base directory if it doesn't exist
        self.base_directory.mkdir(parents=True, exist_ok=True)
    
    def clone_student_repo(
        self, 
        student: Student, 
        assignment: str,
        force: bool = False
    ) -> CloneResult:
        """
        Clone a single student's repository.
        
        Args:
            student: Student object
            assignment: Assignment name
            force: If True, delete existing directory and re-clone
            
        Returns:
            CloneResult object
        """
        # Create student directory
        student_dir = self.base_directory / student.username
        student_dir.mkdir(parents=True, exist_ok=True)
        
        # Repository path
        repo_path = student_dir / assignment
        
        # Check if repo already exists
        if repo_path.exists():
            if force:
                # Remove existing directory
                shutil.rmtree(repo_path)
            else:
                return CloneResult(
                    student=student,
                    success=True,
                    repo_path=repo_path,
                    error=None
                )
        
        # Get repository URL
        repo_url = student.get_repo_url(self.gitlab_host, assignment)
        
        try:
            # Clone the repository
            Repo.clone_from(repo_url, str(repo_path))
            
            return CloneResult(
                student=student,
                success=True,
                repo_path=repo_path,
                error=None
            )
        except GitCommandError as e:
            # Clone failed
            error_msg = str(e)
            
            # Clean up partial clone if it exists
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            return CloneResult(
                student=student,
                success=False,
                repo_path=None,
                error=error_msg
            )
        except Exception as e:
            # Unexpected error
            error_msg = f"Unexpected error: {str(e)}"
            
            # Clean up partial clone if it exists
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            return CloneResult(
                student=student,
                success=False,
                repo_path=None,
                error=error_msg
            )
    
    def clone_all_repos(
        self,
        students: List[Student],
        assignment: str,
        force: bool = False
    ) -> List[CloneResult]:
        """
        Clone repositories for all students.
        
        Args:
            students: List of Student objects
            assignment: Assignment name
            force: If True, delete existing directories and re-clone
            
        Returns:
            List of CloneResult objects
        """
        results = []
        
        for student in students:
            result = self.clone_student_repo(student, assignment, force)
            results.append(result)
        
        return results
    
    def get_clone_summary(self, results: List[CloneResult]) -> dict:
        """
        Get a summary of clone results.
        
        Args:
            results: List of CloneResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
    
    def __repr__(self) -> str:
        """String representation of the cloner."""
        return f"RepositoryCloner(base_dir='{self.base_directory}', host='{self.gitlab_host}')"
