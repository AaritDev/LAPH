# Contributing to L.A.P.H.

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and abide by The [Code of Conduct](CODE_OF_CONDUCT.md).

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
- MAJOR: Breaking changes to CLI or architecture
- MINOR: New features (backward compatible) — typically Phase rollouts
- PATCH: Bug fixes, prompt tweaks, minor improvements

Update in `core/__version__.py` when releasing.

### Semantic Versioning for L.A.P.H.

- **Patch (0.1.x):** Bug fixes, prompt tweaks, minor runner improvements
- **Minor (0.x.0):** New Phase features (vision loop, multi-model routing, SQLite history)
- **Major (x.0.0):** Breaking CLI changes, complete architecture overhaul

## Git Workflow

### Branching Model

L.A.P.H. uses a two-branch stability model:

```
main ──────────────────────────────●─────────── (v0.1.0)
                                   │
dev  ─────●──────●──────●──────────●──────●────
          │      │      │
         feat/  fix/   feat/
         vision  bug    cli
```

- **`main`** — Always stable and releasable. Receives merges only from `dev` at release.
- **`dev`** — Active development branch. Create feature branches from here.
- **Feature branches** — Named `feat/`, `fix/`, `hotfix/`, or `docs/`. Merge back to `dev` via PR.

### Creating Feature Branches

```bash
# Start from dev (ensure it's up to date)
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feat/add-vision-feedback
# or
git checkout -b fix/spinner-race-condition
```

### Merging to dev

Push your branch and create a pull request to `dev`. After review and tests pass:

```bash
git checkout dev
git pull origin dev
git merge --no-ff feat/add-vision-feedback -m "feat: add vision feedback loop"
git push origin dev
```

The `--no-ff` flag preserves the feature branch as a clear commit boundary in history.

## Release Process

The release workflow combines version bumping, changelog updates, stable merges, and tagging:

### 1. Prepare the Release

On the `dev` branch, bump the version string in `core/__version__.py`:

```python
__version__ = "0.2.0"  # Update from "0.1.0"
```

### 2. Update Changelog

Move all items from `[Unreleased]` section to a new `[0.2.0] - YYYY-MM-DD` section in `CHANGELOG.md`:

```markdown
## [0.2.0] - 2025-02-15

### Added
- Vision feedback loop with screenshot analysis
- Multi-model dynamic routing

### Fixed
- Spinner race condition in GUI

## [0.1.0] - 2025-01-15
...
```

### 3. Commit Version Bump

```bash
git add core/__version__.py CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
```

### 4. Merge dev → main

Switch to `main` and merge `dev` with a release commit:

```bash
git checkout main
git pull origin main
git merge dev --no-ff -m "release: v0.2.0"
```

The `--no-ff` flag creates a clear merge commit marking the release boundary.

### 5. Create Annotated Tag

```bash
git tag -a v0.2.0 -m "Phase 2: vision feedback loop and multi-model routing"
```

Annotated tags (with `-a`) store tagger info and timestamp — important for collaboration.

### 6. Push Everything

```bash
git push origin main dev --tags
```

### 7. Create GitHub Release

On GitHub, go to **Releases** and create a new release from tag `v0.2.0`. Copy the relevant section from `CHANGELOG.md` as the release notes.

### Example Release Timeline

```bash
# On dev branch, after feature work is complete and merged
git checkout dev
git pull origin dev

# Bump version
sed -i 's/__version__ = "0.1.0"/__version__ = "0.2.0"/' core/__version__.py
# (or edit manually)

# Update CHANGELOG.md
# ... edit file ...

# Commit
git add core/__version__.py CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"

# Merge to main and tag
git checkout main
git merge dev --no-ff -m "release: v0.2.0"
git tag -a v0.2.0 -m "Phase 2 release"

# Push all branches and tags
git push origin main dev --tags
```

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
