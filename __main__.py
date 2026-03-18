"""Entry point for running L.A.P.H. as a module.

Allows invoking the CLI with:
    python -m laph generate "task description"
"""

from core.cli import cli

if __name__ == "__main__":
    cli()
