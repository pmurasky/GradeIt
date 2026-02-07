import click
import sys
import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from tqdm import tqdm
import sys
import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from .config_loader import ConfigLoader
from .student_loader import StudentLoader, Student
from .repo_cloner import RepositoryCloner, CloneResult
from .gradle_runner import GradleRunner, BuildResult
from .test_parser import TestResultParser, ExecutionSummary
from .ai_grader import GradingAssistant, AnthropicClient
from .feedback_generator import FeedbackGenerator, GradingResult


@dataclass
class GradingContext:
    """Holds the context for the grading operation."""
    assignment: str
    solution: str
    config: ConfigLoader
    max_grade: int
    passing_grade: int
    verbose: bool = False
    
    @property
    def students_file(self) -> str | None:
        return self.config.get('students_file')
        
    @property
    def base_directory(self) -> Path:
        return Path(self.config.get('base_directory', 'repos'))
    
    @property
    def output_directory(self) -> Path:
        return Path(self.config.get('output_directory', 'reports'))
        
    @property
    def gitlab_host(self) -> str:
        return self.config.get('gitlab_host', 'gitlab.hfcc.edu')


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
                pass # Skip unreadable files
        return code_files


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

    @staticmethod
    def print_config(ctx: GradingContext):
        """Print configuration summary."""
        click.echo(f"\nAssignment: {ctx.assignment}")
        click.echo(f"Solution: {ctx.solution}")
        click.echo(f"Max Grade: {ctx.max_grade}")
        click.echo(f"Passing Grade: {ctx.passing_grade}")
        click.echo(f"Verbose Mode: {'On' if ctx.verbose else 'Off'}")
        click.echo(f"Students File: {ctx.students_file}")
        click.echo(f"Output Directory: {ctx.config.get('output_directory')}")
        click.echo(f"GitLab Host: {ctx.gitlab_host}")
        click.echo("\n" + "=" * 50)
        click.echo("Starting grading process...\n")

    @staticmethod
    def print_clone_summary(results: List[CloneResult], cloner: RepositoryCloner):
        """Print clone results summary."""
        summary = cloner.get_clone_summary(results)
        click.echo("\nClone Summary:")
        click.echo(f"Total: {summary['total']}")
        click.echo(f"Successful: {summary['successful']}")
        click.echo(f"Failed: {summary['failed']}")
        click.echo(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['failed'] > 0:
            click.echo("\nFailed Clones:")
            for result in results:
                if not result.success:
                    click.echo(f"✗ {result.student.username}: {result.error}")


class GradingPipeline:
    """Executes grading steps for a single student."""
    
    def __init__(self, ctx: GradingContext):
        self.ctx = ctx
        self.gradle = GradleRunner()
        self.parser = TestResultParser()
        self.ai = GradingAssistant(AnthropicClient())
        self.feedback = FeedbackGenerator(str(ctx.output_directory))
        
    def process_student(self, student: Student, repo_path: Path):
        """Run full grading pipeline for a student."""
        click.echo(f"Processing {student.username}...")
        
        # 1. Build
        build_result = self.gradle.run_build(repo_path)
        
        # 2. Test Results
        test_summary = self.parser.parse_results(repo_path)
        
        # 3. AI Grading
        code = SourceCodeReader.read_files(repo_path / "src/main")
        # Read requirements from solution dir if available, else generic
        reqs = "Review code for best practices and correctness."
        ai_result = self.ai.grade_assignment(code, reqs)
        
        # 4. Feedback
        report = self.feedback.generate_report(student, build_result, test_summary, ai_result)
        path = self.feedback.save_report(student, self.ctx.assignment, report)
        click.echo(f"  ✓ Report saved: {path.name}")


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
        cloner = RepositoryCloner(str(ctx.base_directory), ctx.gitlab_host)
        click.echo(f"Running: Cloning repositories...")
        
        results = []
        with tqdm(total=len(students), desc="Cloning", unit="repo") as pbar:
            for student in students:
                result = cloner.clone_student_repo(student, ctx.assignment)
                results.append(result)
                pbar.update(1)
        
        # Simple summary
        success_count = sum(1 for r in results if r.success)
        click.echo(f"Cloned {success_count}/{len(results)} repositories.")
        return results

    @staticmethod
    def run_grading(ctx: GradingContext, results: List[CloneResult]):
        """Run grading for successfully cloned repos."""
        successful_clones = [r for r in results if r.success and r.repo_path]
        
        if not successful_clones:
            click.echo("No repositories to grade.")
            return

        pipeline = GradingPipeline(ctx)
        
        with tqdm(total=len(successful_clones), desc="Grading", unit="student") as pbar:
            for result in successful_clones:
                pbar.set_postfix_str(f"Student: {result.student.username}", refresh=True)
                try:
                    pipeline.process_student(result.student, result.repo_path)
                except Exception as e:
                    click.echo(f"  ✗ Error grading {result.student.username}: {e}")
                pbar.update(1)


@click.command()
@click.option('--assignment', '-a', required=True, help='Assignment name')
@click.option('--solution', '-s', required=True, type=click.Path(exists=True), help='Solution path')
@click.option('--config', '-c', default='config.properties', type=click.Path(), help='Config file')
@click.option('--max-grade', '-m', type=int, help='Max grade')
@click.option('--passing-grade', '-p', type=int, help='Passing grade')
def main(assignment: str, solution: str, config: str, max_grade: int, passing_grade: int):
    """GradeIt CLI Entry Point."""
    click.echo("🎓 GradeIt - AI-Powered Assignment Grading System")
    click.echo("=" * 50)
    
    try:
        cfg = ConfigLoader(config)
        ctx = GradingContext(
            assignment, solution, cfg,
            max_grade if max_grade is not None else cfg.get_int('max_grade', 100),
            passing_grade if passing_grade is not None else cfg.get_int('passing_grade', 60)
        )
        
        students = GradingManager.load_students(ctx)
        clone_results = GradingManager.clone_repos(ctx, students)
        GradingManager.run_grading(ctx, clone_results)
        
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
