import tkinter as tk
from core.gui import LAPH_GUI


def test_gui_instantiates():
    root = tk.Tk()
    root.withdraw()
    gui = LAPH_GUI(root)
    # basic smoke checks
    assert gui.task_entry is not None
    assert gui.output_box is not None
    root.destroy()