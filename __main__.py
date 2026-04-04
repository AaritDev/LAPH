"""Entry point for running L.A.P.H. as a module.

Allows invoking the CLI/GUI with:
    python -m laph gui                    # Launch GUI
    python -m laph "task description"    # Code generation
    python -m laph --help                # Show help
"""

from main import main

if __name__ == "__main__":
    main()
