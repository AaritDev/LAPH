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
    """Route to appropriate interface based on command-line arguments.
    
    Handles routing logic:
    - No args: launches GUI (default)
    - "gui": explicitly launch GUI
    - "install": launch the installer
    - "generate", "cli", "help", etc.: delegate to CLI system
    - Other strings: treat as task description for code generation
    """
    # Default to GUI if no arguments provided
    if len(sys.argv) == 1:
        launch_gui()
        return

    command = sys.argv[1].lower()

    if command == "gui":
        # User explicitly requested GUI
        launch_gui()
    elif command == "install":
        # User explicitly requested installer
        launch_installer()
    elif command in ("generate", "cli", "--help", "-h", "help"):
        # Delegate to CLI system for these known commands
        from core.cli import cli

        sys.argv.pop(1)  # Remove the 'cli' or similar command
        cli()
    else:
        # Treat any other input as a CLI command
        from core.cli import cli

        cli()


def launch_gui():
    """Launch the graphical user interface.
    
    Initializes Tkinter root window and instantiates the LAPH_GUI class
    to display the full GUI interface.
    """
    root = tk.Tk()
    app = LAPH_GUI(root)
    root.mainloop()


def launch_installer():
    """Launch the installer GUI.
    
    Initializes the graphical installer interface from the installer_gui module.
    """
    from core.installer_gui import run_installer_gui

    run_installer_gui()


if __name__ == "__main__":
    main()
