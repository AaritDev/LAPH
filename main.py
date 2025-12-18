"""Main entrypoint for L.A.P.H. — launches the Tkinter GUI and wires main components.

This module contains a simple `main()` function which creates the Tk root, instantiates
the `LAPH_GUI` and runs the Tk main loop. It is intended to be a minimal launcher
so the package can be executed directly as a script.

Usage:
    python main.py

"""

import tkinter as tk
from core.gui import LAPH_GUI

def main():
    """Create the Tk root, initialize the LAPH_GUI, and start the event loop."""
    root = tk.Tk()
    app = LAPH_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
