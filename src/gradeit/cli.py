"""
Command-line interface for GradeIt.
"""

import click
import sys
from typing import List
from dataclasses import dataclass
from .config_loader import ConfigLoader
from .student_loader import StudentLoader, Student
from .repo_cloner import RepositoryCloner, CloneResult


@dataclass
class GradingContext:
    """Holds the context for the grading operation."""
    assignment: str
    solution: str
    config: ConfigLoader
    max_grade: int
    passing_grade: int
    
    @property
    def students_file(self) -> str | None:
        return self.config.get('students_file')
        
    @property
    def base_directory(self) -> str | None:
        return self.config.get('base_directory')
        
    @property
    def gitlab_host(self) -> str:
        return self.config.get('gitlab_host', 'gitlab.hfcc.edu')


class MessageHandler:
    """Handles CLI output messages."""
    
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
        if not ctx.base_directory:
            raise ValueError("base_directory not defined in config")
            
        cloner = RepositoryCloner(ctx.base_directory, ctx.gitlab_host)
        click.echo(f"Running: Cloning repositories for {ctx.assignment}...")
        
        results = cloner.clone_all_repos(students, ctx.assignment)
        MessageHandler.print_clone_summary(results, cloner)
        return results


@click.command()
@click.option('--assignment', '-a', required=True, help='Assignment name')
@click.option('--solution', '-s', required=True, type=click.Path(exists=True), help='Solution path')
@click.option('--config', '-c', default='config.properties', type=click.Path(), help='Config file')
@click.option('--max-grade', '-m', type=int, help='Max grade')
@click.option('--passing-grade', '-p', type=int, help='Passing grade')
def main(assignment: str, solution: str, config: str, max_grade: int, passing_grade: int):
    """GradeIt CLI Entry Point."""
    MessageHandler.print_welcome()
    
    try:
        cfg = ConfigLoader(config)
        click.echo(f"✓ Loaded configuration from: {config}")
        
        ctx = GradingContext(
            assignment, solution, cfg,
            max_grade if max_grade is not None else cfg.get_int('max_grade', 100),
            passing_grade if passing_grade is not None else cfg.get_int('passing_grade', 60)
        )
        
        MessageHandler.print_config(ctx)
        
        students = GradingManager.load_students(ctx)
        GradingManager.clone_repos(ctx, students)
        
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
