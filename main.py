"""Main entrypoint for L.A.P.H. — launches the Tkinter GUI, CLI, or installer.

This module serves as the primary entry point, supporting:
- GUI mode: `python main.py gui` (default)
- CLI mode: `python main.py generate "task description"`
- Installer: `python main.py install`

Usage:
    python main.py gui              # Launch graphical interface
    python main.py generate "task"  # CLI code generation
    python main.py install          # Launch installer
"""

import sys
import tkinter as tk
from core.gui import LAPH_GUI


def main():
    """Route to appropriate interface based on command-line arguments."""
    # Default to GUI if no arguments provided
    if len(sys.argv) == 1:
        launch_gui()
        return

    command = sys.argv[1].lower()

    if command == "gui":
        launch_gui()
    elif command == "install":
        launch_installer()
    elif command in ("generate", "cli", "--help", "-h", "help"):
        # Delegate to CLI system
        from core.cli import cli
        sys.argv.pop(1)  # Remove 'cli' or similar command
        cli()
    else:
        # Treat as CLI command
        from core.cli import cli
        cli()


def launch_gui():
    """Launch the graphical user interface."""
    root = tk.Tk()
    app = LAPH_GUI(root)
    root.mainloop()


def launch_installer():
    """Launch the installer GUI."""
    from core.installer_gui import run_installer_gui
    run_installer_gui()


if __name__ == "__main__":
    main()
