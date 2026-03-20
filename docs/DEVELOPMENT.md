# Development Guide

This guide covers setting up a development environment for L.A.P.H. and contributing to the project.

## Prerequisites

- **Python 3.11+**
- **Ollama 0.6.0+** (for local LLM inference)
- **Git**
- **Virtual environment manager** (venv, conda, or similar)

## Development Setup

### 1. Clone and Create Virtual Environment

```bash
git clone https://github.com/AaritDev/LAPH.git
cd LAPH
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 3. Install Development Dependencies

For testing and code quality tools:

```bash
pip install pytest pytest-cov black flake8 mypy
```

### 4. Configure Ollama

Start Ollama in a separate terminal:

```bash
ollama serve
```

Pull required models:

```bash
ollama pull qwen2.5-coder:7b-instruct
ollama pull qwen3:14b
```

## Project Structure

```
L.A.P.H./
├── core/                 # Main application logic
│   ├── cli.py           # Command-line interface
│   ├── gui.py           # GUI implementation
│   ├── llm_interface.py # LLM communication
│   ├── repair_loop.py   # Core agent loop
│   ├── runner.py        # Task execution
│   └── ...
├── prompts/             # System prompts for models
├── tests/               # Test suite
├── configs/             # Configuration files
└── docker/              # Docker setup
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core

# Run specific test
pytest tests/test_llm_generation.py
```

## Code Style

Follow PEP 8 conventions. Run formatters before committing:

```bash
black core/ tests/
flake8 core/ tests/
```

## Running the Application

### CLI Mode

```bash
python -m laph "your task description"
python -m laph -i 10 "your task"      # Custom iterations
python -m laph -v "your task"         # Verbose output
```

### GUI Mode

```bash
python -m laph gui
```

### Debug Mode

Set environment variables for additional logging:

```bash
export LAPH_DEBUG=1
export LAPH_LOG_LEVEL=DEBUG
python -m laph "your task"
```

## Contributing

Before submitting a pull request:

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write tests for new functionality
4. Run the test suite: `pytest`
5. Format your code: `black core/ tests/`
6. Commit and push your changes
7. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

## Common Issues

### Connection Refused

**Problem:** `Error: Connection refused` when running tasks

**Solution:**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run LAPH
python -m laph "your task"
```

### Out of Memory

**Problem:** GPU runs out of memory during generation

**Solution:** Use smaller models
```bash
python -m laph -m qwen2.5-coder:7b-instruct "your task"
```

### Tests Fail

**Problem:** Tests fail with import errors

**Solution:** Ensure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate
pip install -r requirements.txt
pytest
```

## Architecture Notes

The core application flow:

1. **CLI/GUI Input** → User provides task description
2. **Thinker Model** → Analyzes task and creates solution plan
3. **Coder Model** → Generates Python code
4. **Validator** → Tests generated code
5. **Repair Loop** → Iteratively fixes issues if needed

See `core/repair_loop.py` for detailed implementation.

## Performance Profiling

To profile the application:

```bash
python -m cProfile -s cumtime -m laph "simple task" > profile.txt
```

## Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LAPH_DEBUG=1
python -m laph "your task"
```

## Questions?

- Open an issue on [GitHub](https://github.com/AaritDev/LAPH/issues)
- Check existing issues and discussions
- Review code comments in `core/` for implementation details
