# General Coding Practices and Standards

## Overview
This document outlines language-agnostic coding practices, testing expectations, and development principles for the GradeIt project.

## General Principles

### YAGNI (You Aren't Gonna Need It)
**Do not implement features, classes, methods, or infrastructure until you actually need them.**

- **Only create what is needed now**: Don't build for hypothetical future requirements
- **No speculative generality**: Don't add abstraction layers "just in case"
- **Create directories/packages when needed**: Don't create empty package structures upfront
- **Add dependencies when required**: Don't add libraries until you actually use them
- **Incremental development**: Build the simplest thing that works, then refactor when needed

**Benefits:**
- Less code to maintain
- Simpler codebase
- Faster development
- Easier to understand
- Reduced over-engineering

**Examples:**
- ✅ Create a `User` class when you need to store user data
- ❌ Create `User`, `UserFactory`, `UserBuilder`, `UserValidator` upfront "just in case"
- ✅ Add a package when you have classes to put in it
- ❌ Create all packages for the entire architecture before writing any code
- ✅ Add a dependency when you need its functionality
- ❌ Add every dependency you might possibly need

### Code Quality
- Write clean, readable, and maintainable code
- Follow SOLID principles
- Prefer composition over inheritance
- **Keep functions/methods small and focused (single responsibility)**
- **Maximum function length: 15 lines of code** (excluding blank lines and docstrings)
  - If a function exceeds 15 lines, extract helper functions
  - This enforces single responsibility and improves testability
  - Exception: Test functions may be longer if needed for clarity
- Avoid code duplication (DRY principle)
- Use meaningful names for variables, functions, and classes

### Single Responsibility Principle (SRP)
**Each class/module should have only one reason to change.**

- **Limit private methods**: If a class has many private methods, it's likely doing too much
  - Private methods often indicate hidden responsibilities that should be extracted
  - Extract complex private logic into separate, testable classes or functions
  - Aim for 0-2 private methods per class; more suggests refactoring needed
- **Extract functionality into separate classes/modules** when:
  - Logic becomes complex enough to need dedicated testing
  - A method or group of methods serves a distinct purpose
  - You find yourself wanting to test private methods directly
- **Prefer small, focused classes** over large classes with many private methods
- **Benefits**:
  - Easier to test (public interfaces instead of private methods)
  - Better separation of concerns
  - More reusable components
  - Clearer dependencies

**Examples:**
- ❌ **Bad**: `UserService` with private methods: `_validate_email()`, `_hash_password()`, `_send_welcome_email()`, `_log_activity()`
  - Too many responsibilities (validation, security, email, logging)
  - Private methods can't be tested independently
- ✅ **Good**: Separate classes/modules: `EmailValidator`, `PasswordHasher`, `EmailService`, `ActivityLogger`
  - Each class has single responsibility
  - All functionality is testable
  - Can be reused independently

**When to use private methods:**
- Simple helper methods (1-3 lines) that aid readability
- Methods that truly only exist to support the single public responsibility
- If you have > 2 private methods, consider extraction

### Documentation
- All public APIs must have comprehensive documentation (Docstrings)
- Include examples in documentation where appropriate
- Document non-obvious implementation decisions with inline comments
- Keep README and other documentation up-to-date

### Error Handling
- Use specific exception types, not generic `Exception`
- Document all raised exceptions in docstrings
- Catch exceptions at appropriate levels
- Provide meaningful error messages
- Log errors with appropriate context
- Don't swallow exceptions silently (avoid bare `except: pass`)

### Logging
- Use appropriate log levels:
  - **ERROR**: Application errors, exceptions
  - **WARN**: Recoverable issues, deprecated usage
  - **INFO**: Significant events, lifecycle changes
  - **DEBUG**: Detailed diagnostic information
- Include context in log messages
- No sensitive information in logs (passwords, tokens)

## Testing Standards

### Test Coverage Requirements
- **Minimum Coverage**: 80% overall
- **Critical Paths**: 100% coverage for:
  - Grading logic
  - Git operations
  - Build execution
- **Branch Coverage**: Minimum 75%

### Test Types

**1. Unit Tests**
- Test individual classes/functions in isolation
- Mock all external dependencies
- Fast execution (< 1 second per test)
- Example: `test_student_loader.py`, `test_grade_calculator.py`

**2. Integration Tests**
- Test component interactions
- May use real implementations (with test doubles for external services like GitLab/Anthropic)
- Example: `test_repo_cloner_integration.py`

**3. End-to-End Tests**
- Test complete workflows
- Use real projects as fixtures
- Example: `test_full_grading_flow.py`

### Test Naming Convention
Use descriptive test names that explain what is being tested:

**Good examples:**
- `test_should_clone_valid_repo()`
- `test_should_raise_error_when_config_missing()`
- `test_should_parse_grade_from_output()`

**Avoid generic names:**
- `test_1()`
- `test_cloner()`

### Test Structure (Given-When-Then)
```python
def test_should_filter_out_invalid_students(self):
    # Given - Setup test data and mocks
    students = ["valid-group", "invalid-group"]
    loader = StudentLoader(students)
    
    # When - Execute the code under test
    result = loader.load()
    
    # Then - Assert expected outcomes
    assert len(result) == 1
    assert result[0].group == "valid-group"
```

### Mocking Guidelines
- Mock external dependencies (HTTP clients, file system, databases, subprocess calls)
- Don't mock value objects or simple data classes
- Verify important interactions with mocks
- Use realistic test data

### Test Data and Fixtures
- Store test data in `tests/fixtures/` or use `pytest.fixture`
- Use realistic but minimal examples
- Document any non-obvious test data

### Assertions
- Use descriptive assertion messages (pytest provides good default output)
- Use standard `assert` statements (idiomatic pytest)

### Test Independence
- Each test must be independent and isolated
- No shared mutable state between tests (use fixtures)
- Tests should pass when run individually or as a suite

## Code Review Checklist

### Functionality
- [ ] Code meets requirements
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs or logic errors

### Code Quality
- [ ] Follows coding standards
- [ ] No code duplication
- [ ] Appropriate use of design patterns
- [ ] SOLID principles applied
- [ ] **All functions are 15 lines or fewer**
- [ ] **Commit is focused on single logical change** (micro commit)

### Testing
- [ ] Adequate test coverage (minimum 80%)
- [ ] Tests are meaningful and not just for coverage
- [ ] Tests follow naming conventions

### Documentation
- [ ] Public APIs are documented (Docstrings)
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed
- [ ] Type hints used throughout

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation for external data
- [ ] Secure handling of sensitive information (API keys)

### Performance
- [ ] No obvious performance issues
- [ ] No unnecessary object creation in loops

## Git Commit Standards

### Micro Commits Philosophy
**Practice micro commits** - commit early and often with small, focused changes:

- **Commit frequently**: After completing each small unit of work
- **One logical change per commit**: Each commit should represent a single, coherent change
- **Benefits**:
  - Easier code review
  - Simpler debugging and git bisect
  - Better project history and documentation
  - Easy to revert specific changes
  - Less risk of losing work
  
**Examples of micro commit granularity**:
- Add a single dataclass
- Implement one function
- Add tests for one function
- Refactor one function
- Update documentation for one component
- Fix one specific bug

**Avoid**:
- Large commits with multiple unrelated changes
- Batching many files into one commit
- Waiting until end of day to commit
- Committing broken/non-compiling code (unless WIP branch)

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no functionality change)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, tooling

### Examples
```
feat(cloner): add support for SSH keys

Integrate SSH key authentication for GitLab cloning.
This allows accessing private repositories securely.

Closes #123
```

```
fix(parser): handle empty report files

Previously, the parser would crash on empty XML files.
Now it logs a warning and returns an empty summary.
```

## Dependencies

### Dependency Management
- Keep dependencies up-to-date (`requirements.txt` / `pyproject.toml`)
- Avoid dependencies with known vulnerabilities
- Prefer well-maintained libraries

## Security Practices

### Secrets Management
- Never commit secrets, API keys, passwords
- Use environment variables (e.g., `.env` files) for sensitive data
- Rotate credentials regularly

### Input Validation
- Validate all external input (files, user input)
- Sanitize data before use

## Questions or Clarifications?

If anything in these standards is unclear or needs discussion, please:
1. Open an issue for discussion
2. Propose changes via pull request
3. Document decisions and update this file

---

**Last Updated**: February 6, 2026
**Version**: 1.1 (Python Adaptation)