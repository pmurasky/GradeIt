# Coding Standards

## Overview
This document serves as the entry point for coding standards and practices for the GradeIt project.

The standards have been organized into separate documents for clarity:

## Documentation Structure

### 📘 [CODING_PRACTICES.md](./CODING_PRACTICES.md)
**General language-agnostic coding practices**

Contains universal principles and practices that apply regardless of programming language:
- YAGNI (You Aren't Gonna Need It)
- Code Quality principles
- Single Responsibility Principle (SRP)
- Testing Standards (unit, integration, E2E)
- Test structure and naming conventions
- Code Review Checklist
- Git Commit Standards (micro commits)
- Security Practices

**Read this document for**: General software engineering best practices, testing philosophy, and team workflow.

### 🐍 [PYTHON_STANDARDS.md](./PYTHON_STANDARDS.md)
**Python-specific coding standards**

Contains Python-specific conventions, styles, and best practices:
- PEP 8 Naming conventions
- Type Hinting
- Docstring formatting (Google Style)
- Pytest usage
- Project Structure
- Dependency Management
- Modern Python features

**Read this document for**: Python implementation details, syntax conventions, and ecosystem best practices.

## Quick Reference

### For New Team Members
1. Start with [CODING_PRACTICES.md](./CODING_PRACTICES.md) to understand our general philosophy
2. Review [PYTHON_STANDARDS.md](./PYTHON_STANDARDS.md) for Python-specific conventions
3. Reference both during code reviews

### Key Principles (Summary)

#### YAGNI
- Only create what you need now
- No speculative development

#### Code Quality
- **25 lines max per function/method** (excluding blanks/docstrings)
- **0-2 private methods per class/module** (SRP guideline)
- Comprehensive testing (80%+ coverage)

#### Git Workflow
- **Micro commits**: One logical change per commit
- Test-Driven Development (TDD) recommended
- Code review before every commit

#### Testing
- Write tests first (TDD)
- 80% minimum coverage
- 100% for critical paths
- Given-When-Then structure

## Project Package Structure

This project follows the `src` layout pattern:

```
src/
└── gradeit/
    ├── ai/           # AI integration components
    ├── build/        # Build system integration (Gradle)
    ├── core/         # Core domain logic
    ├── scm/          # Source control (GitLab)
    └── utils/        # Shared utilities
```

## Questions or Updates?

If anything is unclear or needs discussion:
1. Open an issue for discussion
2. Propose changes via pull request
3. Update relevant document(s)

---

**Last Updated**: February 6, 2026
**Version**: 2.1 (Python Standard)