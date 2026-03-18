# Contributing to L.A.P.H.

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- Virtual environment (`venv`)
- Ollama (for testing LLM integration)

### Development Setup

```bash
git clone https://github.com/AaritDev/LAPH.git
cd LAPH
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install base + dev dependencies
pip install -r requirements.txt
pip install black ruff mypy pytest pytest-cov pre-commit
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This ensures code is automatically formatted and checked before commits.

## Code Style

### Formatting

Use **Black** for all Python code:

```bash
black core/ tests/
```

- Line length: **88 characters** (Black default)
- Spaces: 4 per indentation level
- No trailing whitespace

### Linting

Use **Ruff** for static analysis:

```bash
ruff check core/ tests/
ruff check --fix core/ tests/  # Auto-fix issues
```

### Type Hints

All functions must have complete type hints:

```python
from typing import Optional, Tuple

def run_code(self, code: str) -> Tuple[str, str, int]:
    """Execute Python code in sandboxed environment.
    
    Args:
        code: Python source code to execute.
        
    Returns:
        Tuple of (stdout, stderr, exit_code).
    """
    pass
```

Run type checker:

```bash
mypy core/ --strict
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code reorganization (no behavior change)
- `docs:` Documentation only
- `test:` Tests only
- `chore:` Tooling, dependencies, etc.
- `perf:` Performance improvement

### Examples

```
feat(cli): add --output flag for saving generated code

Users can now save generated code to a file using the -o/--output option.

Closes #42
```

```
fix(runner): prevent tempfile resource leak

Wrap file deletion in finally block and handle OSError gracefully.
Also adds platform check for Windows (no resource limits available).
```

## Branch Naming

Create feature branches with clear names:

```
feature/add-vision-feedback
bugfix/fix-spinner-race-condition
hotfix/critical-security-patch
docs/update-architecture-guide
```

Never commit directly to `main`.

## Pull Requests

### Before Submitting

1. **Run tests:** `pytest tests/ -v`
2. **Format code:** `black core/ tests/`
3. **Type check:** `mypy core/ --strict`
4. **Lint:** `ruff check core/ tests/`
5. **Update docs:** If adding features, update relevant docs
6. **Add tests:** New code must have test coverage

### PR Template

```markdown
## Description
Brief description of changes.

## Related Issues
Closes #ISSUE_NUMBER

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] Performance improvement

## Testing
How was this tested? Include commands/steps to verify.

## Checklist
- [ ] Code formatted with Black
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Type hints added (`mypy core/ --strict`)
- [ ] Documentation updated
- [ ] No new warnings from Ruff
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_repair_loop.py::test_run_task -v

# With coverage
pytest tests/ --cov=core --cov-report=html
```

### Writing Tests

Use `pytest` and follow the existing test patterns:

```python
def test_run_code_success():
    """Test successful code execution."""
    runner = CodeRunner()
    out, err, code = runner.run_code("print('hello')")
    assert out == "hello\n"
    assert err == ""
    assert code == 0
```

**Coverage requirement:** Minimum 80% code coverage.

## Documentation

### Docstring Format

Use **Google style** docstrings for all public functions/classes:

```python
def generate_spec(
    self,
    task: str,
    code: Optional[str] = None,
    error: Optional[str] = None,
) -> str:
    """Generate specification from task description.
    
    Uses the Thinker model to analyze the task and produce
    a detailed specification for code generation.
    
    Args:
        task: Natural language task description.
        code: Previously generated code (for context).
        error: Previous error message (if retrying).
        
    Returns:
        JSON specification with requirements and constraints.
        
    Raises:
        ConnectionError: If Ollama endpoint is unreachable.
        ValueError: If task description is empty.
        
    Example:
        >>> agent = RepairLoop(logger)
        >>> spec = agent.generate_spec("write fibonacci")
        >>> "fibonacci" in spec.lower()
        True
    """
    pass
```

### Sections

- **Args:** Parameter descriptions with types
- **Returns:** Description of return value(s)
- **Raises:** Possible exceptions
- **Example:** Usage example (if applicable)

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Update in `core/__version__.py` when releasing.

## Release Process

1. Update `CHANGELOG.md` with new changes
2. Bump version in `core/__version__.py`
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. Create GitHub release with changelog

## Reporting Issues

Use GitHub Issues with descriptive titles:

- ✅ Good: "TextWidget rendering lag when streaming 10KB+ output"
- ❌ Bad: "slow" or "UI doesn't work"

Include:

- What you did
- What you expected
- What actually happened
- System info (OS, Python version, VRAM, etc.)
- Logs/error messages

## Questions?

- [GitHub Discussions](https://github.com/AaritDev/LAPH/discussions)
- Create an issue labeled `question`

---

Thank you for contributing! 🎉
