"""GUI unit tests (smoke and basic behavior checks).

These tests instantiate `LAPH_GUI` in a hidden Tk root to assert basic
behaviors (widget creation, iteration clamping, and streaming callbacks).
"""

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


def test_iteration_clamping():
    root = tk.Tk()
    root.withdraw()
    gui = LAPH_GUI(root)
    gui.max_iters_var.set(100)
    gui._on_iter_focus_out()
    assert gui.max_iters_var.get() == 60

    gui.max_iters_var.set(-10)
    gui._on_iter_focus_out()
    assert gui.max_iters_var.get() == 0

    root.destroy()


def test_stream_callback_clears_and_shows_prompts():
    root = tk.Tk()
    root.withdraw()
    gui = LAPH_GUI(root)
    gui.stream_callback("Do X", "thinker_prompt")
    assert "Thinker Prompt" in gui.thinker_box.get(1.0, tk.END)
    gui.stream_callback("Spec details", "coder_prompt")
    assert "# Spec" in gui.output_box.get(1.0, tk.END)
    root.destroy()