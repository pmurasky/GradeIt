"""
Command-line interface for GradeIt.
"""

import click
from pathlib import Path
from .config_loader import ConfigLoader
from .student_loader import StudentLoader
from .repo_cloner import RepositoryCloner


@click.command()
@click.option(
    '--assignment',
    '-a',
    required=True,
    help='Assignment name (e.g., fizzbuzz)'
)
@click.option(
    '--solution',
    '-s',
    required=True,
    type=click.Path(exists=True),
    help='Path to the solution directory'
)
@click.option(
    '--config',
    '-c',
    default='config.properties',
    type=click.Path(exists=True),
    help='Path to config.properties file (default: config.properties)'
)
@click.option(
    '--max-grade',
    '-m',
    type=int,
    help='Maximum grade (overrides config default)'
)
@click.option(
    '--passing-grade',
    '-p',
    type=int,
    help='Passing grade threshold (overrides config default)'
)
def main(assignment: str, solution: str, config: str, max_grade: int, passing_grade: int):
    """
    GradeIt - AI-Powered Assignment Grading System
    
    Automatically grades student Java assignments from GitLab repositories.
    """
    click.echo("🎓 GradeIt - AI-Powered Assignment Grading System")
    click.echo("=" * 50)
    
    # Load configuration
    try:
        cfg = ConfigLoader(config)
        click.echo(f"✓ Loaded configuration from: {config}")
    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        return 1
    
    # Override grading parameters if provided
    max_grade_value = max_grade if max_grade is not None else cfg.get_int('max_grade', 100)
    passing_grade_value = passing_grade if passing_grade is not None else cfg.get_int('passing_grade', 60)
    
    # Display configuration
    click.echo(f"\nAssignment: {assignment}")
    click.echo(f"Solution: {solution}")
    click.echo(f"Max Grade: {max_grade_value}")
    click.echo(f"Passing Grade: {passing_grade_value}")
    click.echo(f"Students File: {cfg.get('students_file')}")
    click.echo(f"Output Directory: {cfg.get('output_directory')}")
    click.echo(f"GitLab Host: {cfg.get('gitlab_host')}")
    
    click.echo("\n" + "=" * 50)
    click.echo("Starting grading process...\n")
    
    # Initialize components
    try:
        # Load students
        click.echo("Running: Loading student data...")
        students_file = cfg.get('students_file')
        if not students_file:
            raise ValueError("students_file not defined in config")
            
        student_loader = StudentLoader(students_file)
        students = student_loader.load_students()
        click.echo(f"✓ Loaded {len(students)} students")
        
        # Initialize cloner
        base_dir = cfg.get('base_directory')
        if not base_dir:
            raise ValueError("base_directory not defined in config")
        
        # Resolve config path relative to config file if base_directory uses relative path
        # But ConfigLoader handles absolute path expansion if configured correctly
        # Here we trust ConfigLoader's substitution
            
        gitlab_host = cfg.get('gitlab_host', 'gitlab.hfcc.edu')
        cloner = RepositoryCloner(base_dir, gitlab_host)
        
        # Clone repositories
        click.echo(f"Running: Cloning repositories for {assignment}...")
        results = cloner.clone_all_repos(students, assignment)
        
        # Display summary
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
            
    except Exception as e:
        click.echo(f"\n✗ Error during execution: {e}", err=True)
        return 1
    
    return 0


if __name__ == '__main__':
    main()
