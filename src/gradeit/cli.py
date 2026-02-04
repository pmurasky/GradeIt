"""
Command-line interface for GradeIt.
"""

import click
from pathlib import Path
from .config_loader import ConfigLoader


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
    
    # TODO: Implement grading workflow
    click.echo("⚠ Grading workflow not yet implemented")
    
    return 0


if __name__ == '__main__':
    main()
