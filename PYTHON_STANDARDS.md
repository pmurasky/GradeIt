# Python Coding Standards

## Naming Conventions
Follow **PEP 8** naming conventions:
- **Classes**: `PascalCase` (e.g., `StudentLoader`)
- **Functions/Methods**: `snake_case` (e.g., `load_students`)
- **Variables**: `snake_case` (e.g., `student_list`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_RETRIES`)
- **Private Members**: `_leading_underscore` (e.g., `_parse_file`)

## Formatting
- **Line Length**: Soft limit 88 characters (Black default), hard limit 100.
- **Indentation**: 4 spaces (no tabs).
- **Imports**: Sorted and grouped (Standard Lib, Third Party, Local).
- **Whitespace**: Follow PEP 8 (spaces around operators, etc.).

## Type Hinting
- **Strict Typing**: Use type hints for all function signatures and class attributes.
- Use `typing` module or built-in types (Python 3.9+ style: `list[str]`, `dict[str, int]`).
- Use `Optional` for values that can be `None`.
- Use `Any` sparingly and only when absolutely necessary.

```python
def calculate_grade(score: int, total: int) -> float:
    pass
```

## Documentation (Docstrings)
- Use **Google Style** docstrings for all modules, classes, and public functions.
- Description should be in imperative mood ("Return the..." not "Returns the...").

```python
def connect_to_db(url: str, timeout: int = 5) -> Connection:
    """
    Connect to the database.

    Args:
        url: The database connection string.
        timeout: Connection timeout in seconds.

    Returns:
        The active database connection.

    Raises:
        ConnectionError: If connection fails.
    """
    pass
```

## Classes and Dataclasses
- Prefer `@dataclass` for simple data containers.
- Use properties (`@property`) instead of explicit getters/setters where appropriate.
- Keep `__init__` simple.

```python
@dataclass
class Student:
    name: str
    id: int
```

## Exception Handling
- Use custom exception classes for domain-specific errors.
- Exception classes should inherit from `Exception` and end with `Error`.

```python
class GradingError(Exception):
    """Base class for grading errors."""
    pass
```

## Testing
- Use **pytest** as the testing framework.
- Use fixtures (`@pytest.fixture`) for setup/teardown.
- Place tests in `tests/` directory mirroring source structure.
- Filenames must start with `test_`.

## Project Structure
Follow a standard Python source layout:

```
project_root/
├── src/
│   └── gradeit/
│       ├── __init__.py
│       └── module.py
├── tests/
│   ├── __init__.py
│   └── test_module.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Dependency Management
- Use a virtual environment (`.venv`).
- Track dependencies in `requirements.txt` (and `requirements-dev.txt` for dev tools).
- Pin versions to ensure reproducibility.

## Python 3.12+ Features
- Utilize modern Python features where they improve readability:
  - F-strings for interpolation.
  - Type union operator `|` (e.g., `str | None`).
  - `match`/`case` for structural pattern matching (if applicable).
