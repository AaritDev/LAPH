# L.A.P.H. — Local Autonomous Programming Helper

**Intelligent code generation agent that iteratively synthesizes and debugs Python code through multi-model AI reasoning.**

Generate working Python code from natural language task descriptions using a self-correcting agent loop with Thinker and Coder models.

## Quick Demo

```bash
git clone https://github.com/AaritDev/LAPH.git
cd LAPH
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m laph "write a function that validates email addresses"
```

## Prerequisites

|------------|----------------------------------------------------|
| Component  | Requirement                                        |
|------------|----------------------------------------------------|
| **Python** | 3.11+                                              |
| **Ollama** | 0.6.0+ (for local LLM inference)                   |
| **OS**     | Ubuntu 22.04+, Fedora 38+, or macOS 12+            |
| **RAM**    | 16GB minimum (8GB usable for app)                  |
| **VRAM**   | 6GB minimum (8GB recommended for smooth operation) |
| **Disk**   | 20GB for models + code                             |
|------------|----------------------------------------------------|

### Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

**Fedora:**
```bash
sudo dnf install python3.11 python3.11-devel
```

**macOS:**
```bash
brew install python@3.11
```

**Ollama:** Download from [ollama.com](https://ollama.com), then:
```bash
ollama pull qwen2.5-coder:7b-instruct
ollama pull qwen3:14b
```

## Quick Start

```bash
git clone https://github.com/AaritDev/LAPH.git
cd LAPH
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m laph --help
```

## Usage

### Command Line

```bash
# Generate code from task description
laph "write a fibonacci sequence generator with memoization"

# Specify iterations
laph -i 15 "parse JSON and extract email addresses"

# Use custom model
laph -m qwen3:14b "implement quicksort algorithm"

# Verbose output
laph -v "create a progress bar using TQDM"

# Save output
laph -o generated_code.py "write binary search"
```

### GUI

```bash
laph gui
```

## Architecture

For detailed system design and agent flow, see the code comments in `core/repair_loop.py` and `core/runner.py`.

## Performance (Estimates)

|--------------------|----------------|-----------|--------------|
| Task Type          | Avg Iterations | Est. Time | Success Rate |
|--------------------|----------------|-----------|--------------|
| Simple functions   | 3-5            | 45-90s    | 95%          |
| Data processing    | 6-10           | 2-4min    | 85%          |
| Complex algorithms | 10-15          | 4-8min    | 75%          |
|--------------------|----------------|-----------|--------------|

## Limitations

- No file I/O (security first)
- No internet access for generated code
- Python only (for now)
- Depends on base model quality
- Context window limited

## Troubleshooting

**Connection refused?**
```bash
ollama serve  # Start Ollama in separate terminal
```

**Out of memory?**
```bash
laph -m qwen2.5-coder:7b-instruct "your task"  # Use smaller model
```

**Need help?**
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contributing guidelines
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Development setup
- [GitHub Issues](https://github.com/AaritDev/LAPH/issues) — Report bugs

## License

GPL-3.0 — See [LICENSE](LICENSE)

## Citation

```bibtex
@software{laph2025,
  title={L.A.P.H.: Local Autonomous Programming Helper},
  author={Aarit},
  year={2025},
  url={https://github.com/AaritDev/LAPH}
}
```

Built with [Ollama](https://ollama.com), [Click](https://click.palletsprojects.com/), and [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap).

## Important
The image ./laph.png was created using generative AI, or the image is AI generated. This project generates code autonomously using Generative AI, the authors are not responsible for the generated output
