"""
Gradle build runner for GradeIt.
Handles execution of Gradle builds for student repositories.
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class BuildResult:
    """Result of a Gradle build execution."""
    
    success: bool
    output: str
    error: Optional[str] = None
    
    def __repr__(self) -> str:
        """String representation of the build result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"BuildResult({status})"


class GradleRunner:
    """Executes Gradle builds for student projects."""
    
    def __init__(self, use_wrapper: bool = True):
        """
        Initialize the Gradle runner.
        
        Args:
            use_wrapper: Whether to use the gradlew wrapper (default: True)
                         If False, uses system 'gradle' command
        """
        self.use_wrapper = use_wrapper
    
    def run_build(self, project_path: Path, task: str = "build") -> BuildResult:
        """
        Run a Gradle task in the specified project directory.
        
        Args:
            project_path: Path to the project root containing build.gradle
            task: Gradle task to run (default: "build")
            
        Returns:
            BuildResult object
        """
        project_path = Path(project_path)
        if not project_path.exists():
            return BuildResult(
                success=False, 
                output="", 
                error=f"Project path does not exist: {project_path}"
            )
        
        # Determine the command to run
        cmd = self._get_gradle_command(project_path)
        if not cmd:
            return BuildResult(
                success=False,
                output="",
                error="Could not determine Gradle command (gradlew not found and not using system gradle)"
            )
            
        cmd.append(task)
        
        try:
            # Run the command
            process = subprocess.run(
                cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            return BuildResult(
                success=process.returncode == 0,
                output=process.stdout + "\n" + process.stderr,
                error=None if process.returncode == 0 else "Build failed with non-zero exit code"
            )
            
        except Exception as e:
            return BuildResult(
                success=False,
                output="",
                error=f"Error executing build: {str(e)}"
            )
    
    def _get_gradle_command(self, project_path: Path) -> Optional[list]:
        """
        Get the command list to execute Gradle.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of command parts (e.g., ['./gradlew']) or None if not found
        """
        if self.use_wrapper:
            # Check for wrapper script
            if os.name == 'nt':
                wrapper = project_path / 'gradlew.bat'
            else:
                wrapper = project_path / 'gradlew'
            
            if wrapper.exists():
                # Ensure it's executable on Unix-like systems
                if os.name != 'nt' and not os.access(wrapper, os.X_OK):
                    try:
                        os.chmod(wrapper, 0o755)
                    except OSError:
                        pass # Attempt to run anyway, or fallback? 
                             # Ideally we should log a warning here.
                
                return [str(wrapper.absolute())]
        
        # Fallback to system gradle if wrapper not found or requested not to use it
        # This is a simple check; in a real scenario we might want to verify 'gradle' is in PATH
        return ['gradle']

    def __repr__(self) -> str:
        """String representation of the runner."""
        return f"GradleRunner(use_wrapper={self.use_wrapper})"
