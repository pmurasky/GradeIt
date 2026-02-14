"""
Command-line interface for GradeIt.
"""

import click
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from tqdm import tqdm
from .config_loader import ConfigLoader
from .student_loader import StudentLoader, Student
from .repo_cloner import RepositoryCloner, CloneResult
from .gradle_runner import GradleRunner, BuildResult
from .test_parser import TestResultParser, ExecutionSummary
from .ai_grader import GradingAssistant
from .ai_clients import AIClientFactory, FallbackAIClient
from .feedback_generator import FeedbackGenerator, GradingResult
from .feedback_reader import FeedbackReader


@dataclass
class GradingContext:
    """Holds the context for the grading operation."""
    config: ConfigLoader
    verbose: bool = False
    assignment: Optional[str] = None
    solution: Optional[str] = None
    max_grade: int = 100
    passing_grade: int = 60
    
    @property
    def students_file(self) -> str | None:
        return self.config.get('students_file')
        
    @property
    def base_directory(self) -> Path:
        return Path(self.config.get('base_directory', 'repos'))
    
    @property
    def repositories_directory(self) -> Path:
        return Path(self.config.get('repositories_directory', 'repos'))
    
    @property
    def output_directory(self) -> Path:
        return Path(self.config.get('output_directory', 'reports'))

    @property
    def solutions_directory(self) -> Path:
        return Path(self.config.get('solutions_directory', 'solutions'))
        
    @property
    def gitlab_host(self) -> str:
        return self.config.get('gitlab_host', 'gitlab.hfcc.edu')


class MessageHandler:
    """Handles CLI output messages."""
    
    @staticmethod
    def log(ctx: GradingContext, message: str):
        """Log debug message if verbose is enabled."""
        if ctx.verbose:
            click.echo(f"[DEBUG] {message}", err=True)

    @staticmethod
    def print_welcome():
        """Print welcome message."""
        click.echo("🎓 GradeIt - AI-Powered Assignment Grading System")
        click.echo("=" * 50)


class SourceCodeReader:
    """Reads source code for AI analysis."""
    
    @staticmethod
    def read_files(path: Path, extension: str = ".java") -> Dict[str, str]:
        """Read all files with extension in path."""
        code_files = {}
        if not path.exists():
            return code_files
            
        for file_path in path.rglob(f"*{extension}"):
            try:
                content = file_path.read_text(errors='replace')
                code_files[file_path.name] = content
            except Exception:
                pass 
    @staticmethod
    def extract_header_comments(content: str) -> str:
        """Extract header comments (Javadoc/Block) from the beginning of the file."""
        content = content.strip()
        if content.startswith("/**") or content.startswith("/*"):
            end_index = content.find("*/")
            if end_index != -1:
                return content[:end_index+2]
        return ""

    @staticmethod
    def read_files(path: Path, extension: str = ".java") -> Dict[str, str]:
        """Read all files with extension in path."""
        code_files = {}
        if not path.exists():
            return code_files
            
        for file_path in path.rglob(f"*{extension}"):
            try:
                content = file_path.read_text(errors='replace')
                code_files[file_path.name] = content
            except Exception:
                pass 
        return code_files


class GradingPipeline:
    """Executes grading steps for a single student."""
    
    def __init__(self, ctx: GradingContext):
        self.ctx = ctx
        self.gradle = GradleRunner()
        self.parser = TestResultParser()
        
        # Initialize AI client with fallback support
        clients = AIClientFactory.create_fallback_clients(ctx.config)
        fallback_client = FallbackAIClient(clients)
        self.ai = GradingAssistant(fallback_client)
        
        self.feedback = FeedbackGenerator(str(ctx.output_directory))
        
    def process_student(self, student: Student, repo_path: Path):
        """Run full grading pipeline for a student."""
        click.echo(f"Processing {student.username}...")
        
        build_result = self.gradle.run_build(repo_path)
        test_summary = self.parser.parse_results(repo_path)
        
        code = SourceCodeReader.read_files(repo_path / "src/main")
        
        # Extract context from student code
        context = {}
        for filename, content in code.items():
            header = SourceCodeReader.extract_header_comments(content)
            if header:
                context[filename] = header

        # Read solution code if available
        solution_code = {}
        if self.ctx.solution:
            solution_path = Path(self.ctx.solution)
            if solution_path.exists():
                solution_code = SourceCodeReader.read_files(solution_path)

        reqs = "Review code for best practices and correctness."
        ai_result = self.ai.grade_assignment(code, reqs, self.ctx.max_grade, solution_code, context)
        
        report = self.feedback.generate_report(student, build_result, test_summary, ai_result)
        path = self.feedback.append_to_file(self.ctx.assignment or "unknown", report)
        click.echo(f"  ✓ Report appended to: {path.name}")

    def process_student_with_replacement(self, student: Student, repo_path: Path):
        """Run grading pipeline and replace existing feedback for a student."""
        click.echo(f"Processing {student.username}...")
        
        build_result = self.gradle.run_build(repo_path)
        test_summary = self.parser.parse_results(repo_path)
        
        code = SourceCodeReader.read_files(repo_path / "src/main")
        
        # Extract context from student code
        context = {}
        for filename, content in code.items():
            header = SourceCodeReader.extract_header_comments(content)
            if header:
                context[filename] = header

        # Read solution code if available
        solution_code = {}
        if self.ctx.solution:
            solution_path = Path(self.ctx.solution)
            if solution_path.exists():
                solution_code = SourceCodeReader.read_files(solution_path)

        reqs = "Review code for best practices and correctness."
        ai_result = self.ai.grade_assignment(code, reqs, self.ctx.max_grade, solution_code, context)
        
        report = self.feedback.generate_report(student, build_result, test_summary, ai_result)
        path = self.feedback.replace_student_feedback(self.ctx.assignment or "unknown", student.username, report)
        click.echo(f"  ✓ Report replaced in: {path.name}")

    def process_missing_submission(self, student: Student):
        """Generate a 0-grade report for missing submissions."""
        build_result = BuildResult(False, "Repository not found. No build attempted.")
        test_summary = ExecutionSummary(0, 0, [], 0)
        ai_result = GradingResult(
            score=0, 
            feedback="**Homework not Completed**\n\nThe repository could not be found. Grade set to 0.", 
            suggestions=["Ensure repository exists.", "Check naming conventions."],
            confidence=1.0
        )
        
        report = self.feedback.generate_report(student, build_result, test_summary, ai_result)
        path = self.feedback.append_to_file(self.ctx.assignment or "unknown", report)
        click.echo(f"  ✓ Zero-grade appended to: {path.name}")


class GradingManager:
    """Orchestrates the grading process."""
    
    @staticmethod
    def load_students(ctx: GradingContext) -> List[Student]:
        """Load students from file."""
        click.echo("Running: Loading student data...")
        if not ctx.students_file:
             raise ValueError("students_file not defined in config")
        loader = StudentLoader(ctx.students_file)
        students = loader.load_students()
        click.echo(f"✓ Loaded {len(students)} students")
        return students

    @staticmethod
    def clone_repos(ctx: GradingContext, students: List[Student]) -> List[CloneResult]:
        """Clone student repositories."""
        if not ctx.assignment:
             raise ValueError("Assignment name required for cloning")

        cloner = RepositoryCloner(str(ctx.repositories_directory), ctx.gitlab_host)
        click.echo(f"Running: Cloning repositories for {ctx.assignment}...")
        
        results = []
        with tqdm(total=len(students), desc="Cloning", unit="repo") as pbar:
            for student in students:
                result = cloner.clone_student_repo(student, ctx.assignment)
                results.append(result)
                pbar.update(1)
        
        # Only count and report on newly cloned repos (not already existing)
        new_clones = [r for r in results if not r.already_existed]
        if new_clones:
            success_count = sum(1 for r in new_clones if r.success)
            click.echo(f"Cloned {success_count}/{len(new_clones)} repositories.")
        return results

    @staticmethod
    def run_grading(ctx: GradingContext, students: List[Student]):
        """Run grading for cloned repos."""
        pipeline = GradingPipeline(ctx)
        
        # Sort students by username for consistent feedback order
        students.sort(key=lambda s: s.username.lower())
        
        MessageHandler.log(ctx, f"Starting grading for {len(students)} students")
        
        # Read existing feedback to check who needs grading
        feedback_reader = FeedbackReader()
        feedback_path = ctx.output_directory / f"{ctx.assignment}_Feedback.md"
        existing_feedback = feedback_reader.read_feedback_file(feedback_path)
        
        skip_count = 0
        regrade_count = 0
        
        with tqdm(total=len(students), desc="Grading", unit="student") as pbar:
            for student in students:
                pbar.set_postfix_str(f"Student: {student.username}", refresh=True)
                repo_path = ctx.repositories_directory / student.username / ctx.assignment
                
                # Check if student already has feedback
                student_feedback = feedback_reader.find_student_feedback(student.username, existing_feedback)
                
                # Determine if grading should be skipped
                if student_feedback and not student_feedback.is_missing_repo:
                    # Student has valid feedback, skip grading
                    MessageHandler.log(ctx, f"Skipping {student.username} - already graded")
                    skip_count += 1
                    pbar.update(1)
                    continue
                
                # Check if this is a re-grade scenario (missing repo that now exists)
                is_regrade = student_feedback and student_feedback.is_missing_repo and repo_path.exists()
                if is_regrade:
                    click.echo(f"  ↻ Re-grading {student.username} (repository now exists)")
                    regrade_count += 1
                
                # Proceed with grading
                if repo_path.exists():
                     try:
                        MessageHandler.log(ctx, f"Processing {student.username}")
                        
                        if is_regrade:
                            # Replace existing feedback instead of appending
                            pipeline.process_student_with_replacement(student, repo_path)
                        else:
                            # Normal processing (append)
                            pipeline.process_student(student, repo_path)
                     except Exception as e:
                        click.echo(f"  ✗ Error grading {student.username}: {e}")
                        MessageHandler.log(ctx, f"Error: {e}")
                else:
                     click.echo(f"  ⚠ Missing repo for {student.username}: Generating 0 grade")
                     pipeline.process_missing_submission(student)
                pbar.update(1)
        
        # Print summary
        if skip_count > 0:
            click.echo(f"\nSkipped {skip_count} student(s) with existing grades.")
        if regrade_count > 0:
            click.echo(f"Re-graded {regrade_count} student(s) whose repositories were previously missing.")


@click.group()
@click.option('--config', '-c', default='config.properties', type=click.Path(), help='Config file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """GradeIt - AI-Powered Assignment Grading System"""
    MessageHandler.print_welcome()
    try:
        cfg = ConfigLoader(config)
        ctx.obj = GradingContext(config=cfg, verbose=verbose)
    except Exception as e:
        click.echo(f"✗ Configuration Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', required=True, help='Assignment name')
@click.pass_context
def clone(ctx, assignment):
    """Clone student repositories."""
    g_ctx: GradingContext = ctx.obj
    g_ctx.assignment = assignment
    
    try:
        students = GradingManager.load_students(g_ctx)
        GradingManager.clone_repos(g_ctx, students)
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', required=True, help='Assignment name')
@click.option('--solution', '-s', required=True, help='Solution folder name (in solutions_directory)')
@click.option('--max-grade', '-m', default=100, help='Maximum grade for the assignment (default: 100)')
@click.pass_context
def grade(ctx, assignment, solution, max_grade):
    """Grade cloned repositories."""
    g_ctx: GradingContext = ctx.obj
    g_ctx.assignment = assignment
    
    # Resolve solution path
    sol_path = g_ctx.solutions_directory / solution
    if not sol_path.exists():
        click.echo(f"✗ Solution path not found: {sol_path}", err=True)
        sys.exit(1)
        
    g_ctx.solution = str(sol_path)
    g_ctx.max_grade = max_grade
    
    try:
        students = GradingManager.load_students(g_ctx)
        GradingManager.run_grading(g_ctx, students)
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
