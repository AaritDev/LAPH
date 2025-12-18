"""GUI for L.A.P.H. — creates the main Tkinter/ttkbootstrap interface.

This module defines the `LAPH_GUI` class which assembles the entire user interface:
- Task input and options
- Thinker output window
- Generated code editor-like pane with line numbers
- Log/Status area for LLM and runner messages

It also contains a simple `Tooltip` helper used to show hover tooltips for buttons.

The GUI components are styled with `ttkbootstrap` and connected to the `RepairLoop`
agent to run tasks asynchronously.

"""

import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, SUCCESS, DANGER, WARNING, INFO
import threading
from core.repair_loop import RepairLoop
import tkinter as tk
from tkinter import scrolledtext
from core.logger import Logger
import math
import time


class Tooltip:
    """Simple hover tooltip helper.

    Attaches to a Tk widget and displays a small Toplevel label after a short delay.
    Used sparingly to enrich the UI with contextual help for buttons and controls.
    """

    def __init__(self, widget, text, delay=500):
        """Attach the tooltip to `widget` and set hover delay in milliseconds."""
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)

    def schedule(self, event=None):
        """Schedule showing the tooltip after the configured delay."""
        self.id = self.widget.after(self.delay, self.show)

    def show(self):
        """Create a small borderless Toplevel positioned near the widget and display text."""
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#2b2b2b", fg="#dcdcdc", relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=3)

    def hide(self, event=None):
        """Cancel a scheduled show and destroy any visible tooltip window."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class LAPH_GUI:
    """Main application GUI.

    Responsible for building and managing all UI widgets and responding to user
    actions (starting tasks, displaying streaming output, copying code, etc.)
    """

    def __init__(self, root):
        """Initialize GUI state, logger, and RepairLoop agent and populate widgets."""
        self.root = root
        self.root.title("L.A.P.H. — Local Autonomous Programming Helper")
        self.root.geometry("1400x900")
        self.logger = Logger()
        self.logger.register_callback(self.log_message)
        self.agent = RepairLoop(self.logger)
        self.setup_widgets()

    def setup_widgets(self):
        """Create and layout all UI widgets, panels and connect event handlers."""
        style = tb.Style("superhero")

        # Root background
        self.root.configure(bg="#071426")

        main_frame = tb.Frame(self.root, padding=18, bootstyle="dark")
        main_frame.pack(fill="both", expand=True)

        # Title
        # Futuristic header with subtle glow
        title_frame = tb.Frame(main_frame, bootstyle="dark")
        title_frame.pack(pady=(0, 12), fill="x")
        header_canvas = tk.Canvas(title_frame, height=96, bg="#071426", highlightthickness=0)
        header_canvas.pack(fill="x", expand=True)
        # Draw a glowing arc
        w = 1400
        header_canvas.create_oval(-200, -120, 300, 220, fill="#0ea5a4", outline="", stipple="gray25")
        header_canvas.create_text(100, 34, text="L.A.P.H.", anchor="w", font=("Orbitron", 38, "bold"), fill="#7fffd4")
        header_canvas.create_text(100, 74, text="Local Autonomous Programming Helper", anchor="w", font=("Segoe UI", 12, "italic"), fill="#9ad1e6")

        # Input Frame
        input_frame = tb.Labelframe(main_frame, text="Your Task", padding=16, bootstyle="primary")
        input_frame.pack(fill="x", pady=(0, 16))

        self.task_entry = tb.Entry(input_frame, width=70, font=("Fira Sans", 14))
        self.task_entry.pack(pady=10, padx=5, ipady=10, fill="x", expand=True)
        
        # Options Frame
        options_frame = tb.Frame(input_frame, bootstyle="dark")
        options_frame.pack(fill="x", expand=True)

        tb.Label(options_frame, text="Max Iterations:", font=("Segoe UI", 12), bootstyle="inverse-dark").pack(side="left", padx=(5,5))
        # enforce integer-only and range 0..60
        self.max_iters_var = tk.IntVar(value=10)
        vcmd = (self.root.register(self._validate_iter), '%P')
        self.max_iters_entry = tb.Entry(options_frame, width=10, font=("Fira Sans", 12), textvariable=self.max_iters_var, validate='key', validatecommand=vcmd)
        self.max_iters_entry.pack(side="left", padx=(0, 10))
        self.max_iters_entry.bind('<FocusOut>', self._on_iter_focus_out)

        unlimited_button = tb.Button(options_frame, text="Unlimited", bootstyle="info", command=lambda: self.max_iters_var.set(60))
        unlimited_button.pack(side="left", padx=(0, 20))

        self.run_button = tb.Button(options_frame, text="🚀 Run Task", bootstyle=SUCCESS, command=self.run_task_thread)
        self.run_button.pack(side="right", padx=5)
        Tooltip(self.run_button, "Start the repair loop and generate code")
        
        self.example_button = tb.Button(options_frame, text="🎲 Dice Roller Example", bootstyle=WARNING, command=self.fill_dice_prompt)
        self.example_button.pack(side="right", padx=5)
        Tooltip(self.example_button, "Fill the task box with an example prompt")

        # Main content panes
        paned_window = tb.Panedwindow(main_frame, orient="horizontal", bootstyle="dark")
        paned_window.pack(fill="both", expand=True, pady=(10, 0))

        # Left Paned Window for Thinker and Coder
        left_paned_window = tb.Panedwindow(paned_window, orient="vertical", bootstyle="dark")
        paned_window.add(left_paned_window, weight=1)
        
        # Thinker area
        thinker_frame = tb.Labelframe(left_paned_window, text="Thinker Output", padding=10, bootstyle="info")
        left_paned_window.add(thinker_frame, weight=1)
        self.thinker_box = scrolledtext.ScrolledText(thinker_frame, width=100, height=10, font=("Fira Mono", 11), bg="#0b1720", fg="#9bd6e3", insertbackground="#9bd6e3", borderwidth=0, relief="flat")
        self.thinker_box.pack(pady=5, fill="both", expand=True)

        # Coder area
        coder_frame = tb.Labelframe(left_paned_window, text="Generated Code", padding=8, bootstyle="success")
        left_paned_window.add(coder_frame, weight=2)
        # Create an editor-like area with line numbers
        editor_outer = tb.Frame(coder_frame, bootstyle="dark")
        editor_outer.pack(fill="both", expand=True, pady=5)

        self.linenos = tk.Canvas(editor_outer, width=48, bg="#071426", highlightthickness=0)
        self.linenos.pack(side="left", fill="y")

        self.output_box = scrolledtext.ScrolledText(editor_outer, width=100, height=15, font=("Fira Code", 12), bg="#071426", fg="#cfeffc", insertbackground="#cfeffc", borderwidth=0, relief="flat")
        self.output_box.pack(side="left", fill="both", expand=True)

        # line number update bindings
        self.output_box.bind('<KeyRelease>', self._on_text_change)
        self.output_box.bind('<MouseWheel>', self._on_text_change)

        # Single copy button in the header area (replace previous action buttons)
        header_btns = tb.Frame(coder_frame, bootstyle="dark")
        header_btns.pack(fill="x", pady=(0, 6))
        copy_header = tb.Button(header_btns, text="Copy", command=self.copy_code, bootstyle="info-outline", width=10)
        copy_header.pack(side="right", padx=6)
        Tooltip(copy_header, "Copy the generated code to the clipboard")

        # Log area
        log_frame = tb.Labelframe(paned_window, text="LLM Status & Execution", padding=10, bootstyle="info")
        paned_window.add(log_frame, weight=1)
        self.log_box = scrolledtext.ScrolledText(log_frame, width=100, height=10, font=("Fira Mono", 11), bg="#071426", fg="#9bd6e3", insertbackground="#9bd6e3", borderwidth=0, relief="flat")
        self.log_box.pack(pady=5, fill="both", expand=True)

        status_frame = tb.Frame(main_frame, bootstyle="dark")
        status_frame.pack(fill="x", pady=10)

        self.status_label = tb.Label(status_frame, text="Idle", font=("Fira Sans", 12, "bold"), bootstyle=PRIMARY)
        self.status_label.pack(side="left")

        self.progress = tb.Progressbar(status_frame, bootstyle="info", mode="indeterminate", length=180)
        self.progress.pack(side="left", padx=12)

        self._spinner_running = False
        self._spinner_index = 0

    def copy_code(self):
        """Copy the contents of the generated code output to the clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_box.get(1.0, tk.END))

    def _format_code(self):
        """Lightweight code formatter for the generated code pane.

        Strips trailing spaces and collapses sequences of blank lines to improve
        readability before showing final output to the user.
        """
        # Lightweight formatting: strip trailing spaces and collapse multiple blank lines
        txt = self.output_box.get(1.0, tk.END)
        lines = [l.rstrip() for l in txt.splitlines()]
        # collapse more than 2 consecutive blank lines
        new_lines = []
        blank_count = 0
        for l in lines:
            if l.strip() == "":
                blank_count += 1
            else:
                blank_count = 0
            if blank_count <= 2:
                new_lines.append(l)
        formatted = "\n".join(new_lines).rstrip() + "\n"
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, formatted)
        self._on_text_change()

    def _validate_iter(self, proposed: str) -> bool:
        """Validate iteration entry on each key press: allow empty or integer between 0 and 60."""
        if proposed == "":
            return True
        try:
            v = int(proposed)
        except Exception:
            return False
        return 0 <= v <= 60

    def _on_iter_focus_out(self, event=None):
        """Clamp iterations to 0..60 on focus out."""
        try:
            v = int(self.max_iters_entry.get())
        except Exception:
            # fallback to variable value
            try:
                v = int(self.max_iters_var.get())
            except Exception:
                v = 10
        if v < 0:
            v = 0
        if v > 60:
            v = 60
        self.max_iters_var.set(v)
        # ensure the entry text matches the variable
        self.max_iters_entry.delete(0, tk.END)
        self.max_iters_entry.insert(0, str(v))

    def _on_text_change(self, event=None):
        """Debounce and schedule a line-number update triggered by text or mouse events."""
        # Update line numbers to match the content
        self.root.after(5, self._update_line_numbers)

    def _update_line_numbers(self):
        """Redraw the left-hand line number canvas to reflect the editor content."""
        self.linenos.delete("all")
        i = self.output_box.index("@0,0")
        while True:
            dline = self.output_box.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_number = str(i).split(".")[0]
            self.linenos.create_text(36, y+2, anchor="e", text=line_number, font=("Fira Code", 10), fill="#6bd6c4")
            i = self.output_box.index(f"{i} +1line")

    def _start_spinner(self):
        """Start the progress spinner and kick off the animated indicator."""
        if not self._spinner_running:
            self._spinner_running = True
            self.progress.start(10)
            self._animate_spinner()

    def _stop_spinner(self):
        """Stop the progress spinner and animation."""
        if self._spinner_running:
            self._spinner_running = False
            self.progress.stop()

    def _animate_spinner(self):
        """Animate a simple unicode spinner by rotating through frames on a timer."""
        if not self._spinner_running:
            return
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        self._spinner_index = (self._spinner_index + 1) % len(frames)
        self.status_label.config(text=f"Running... {frames[self._spinner_index]}")
        self.root.after(120, self._animate_spinner)

    def log_message(self, message):
        """Append a log message into the UI log pane, adding spacing for separators."""
        # Make separator messages stand out by adding an extra blank line after them
        self.log_box.insert(tk.END, message)
        if '---' in message or '🎉' in message or '❌' in message:
            self.log_box.insert(tk.END, "\n")
        self.log_box.see(tk.END)

    def stream_callback(self, chunk, source):
        """Handle streaming chunks from LLMs and update the appropriate UI pane.

        `source` indicates the origin or marker such as 'thinker', 'coder', 'coder_start',
        'thinker_prompt', etc. This method routes incoming chunks to the thinker,
        coder, or log panes and handles start/end events.
        """
        # Handle prompt markers and start/end signals so we only show the latest generation
        if source == "thinker_prompt":
            # show only latest thinker prompt
            self.thinker_box.delete(1.0, tk.END)
            self.thinker_box.insert(tk.END, "[Thinker Prompt]\n" + (chunk or ""))
            self.thinker_box.see(tk.END)
            return

        if source == "coder_prompt":
            # show the coder prompt/spec at the top of the code pane and clear previous code
            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, "# Spec:\n" + (chunk or "") + "\n\n")
            self.output_box.see(tk.END)
            return

        if source == "thinker_start":
            # start a new thinker output: clear previous output
            self.thinker_box.delete(1.0, tk.END)
            self.thinker_box.insert(tk.END, "[Thinker Output]\n")
            self.thinker_box.see(tk.END)
            return

        if source == "thinker_end":
            # end of thinker output; nothing else to do
            return

        if source == "coder_start":
            # start a new coder output; ensure previous code is cleared (spec remains)
            # remove any trailing ephemeral markers
            self._on_text_change()
            return

        if source == "coder_end":
            # format the final code and update line numbers
            self._format_code()
            return

        if source == "coder":
            # insert chunked code output
            self.output_box.insert(tk.END, chunk)
            self.output_box.see(tk.END)
            return

        if source == "thinker":
            # insert chunked thinker output
            self.thinker_box.insert(tk.END, chunk)
            self.thinker_box.see(tk.END)
            return

        # Fallback: append to the logs only (avoid cluttering logs with every chunk)
        self.log_box.insert(tk.END, chunk)
        self.log_box.see(tk.END)

    def fill_dice_prompt(self):
        """Place a useful dice-rolling example into the task entry for quick demos."""
        example = (
            "a program that makes a simple dice roller where you can choose any dice with any amount of sides and then roll them, "
            "maybe add extra dice like two 20 sided dices or 1 four sided dice, and 2 six sided dices, all rolling together "
            "(and maybe total all the dices values and also make it so whatever the dice rolls to you can add a custom value to it)"
        )
        self.task_entry.delete(0, "end")
        self.task_entry.insert(0, example)

    def run_task_thread(self):
        """Start `run_task` in a background thread and disable UI controls while running."""
        self.run_button.config(state="disabled")
        self.example_button.config(state="disabled")
        self.log_box.delete(1.0, tk.END)
        self.output_box.delete(1.0, tk.END)
        self.thinker_box.delete(1.0, tk.END)
        threading.Thread(target=self.run_task, daemon=True).start()
        if source == "coder":
            # insert chunked code output
            self.output_box.insert(tk.END, chunk)
            self.output_box.see(tk.END)
            return

        if source == "thinker":
            # insert chunked thinker output
            self.thinker_box.insert(tk.END, chunk)
            self.thinker_box.see(tk.END)
            return

        # Fallback: append to the logs only (avoid cluttering logs with every chunk)
        self.log_box.insert(tk.END, chunk)
        self.log_box.see(tk.END)

    def fill_dice_prompt(self):
        example = (
            "a program that makes a simple dice roller where you can choose any dice with any amount of sides and then roll them, "
            "maybe add extra dice like two 20 sided dices or 1 four sided dice, and 2 six sided dices, all rolling together "
            "(and maybe total all the dices values and also make it so whatever the dice rolls to you can add a custom value to it)"
        )
        self.task_entry.delete(0, "end")
        self.task_entry.insert(0, example)

    def run_task_thread(self):
        self.run_button.config(state="disabled")
        self.example_button.config(state="disabled")
        self.log_box.delete(1.0, tk.END)
        self.output_box.delete(1.0, tk.END)
        self.thinker_box.delete(1.0, tk.END)
        threading.Thread(target=self.run_task, daemon=True).start()

    def run_task(self):
        task = self.task_entry.get()
        try:
            max_iters = int(self.max_iters_var.get())
        except Exception:
            max_iters = 10
            self.logger.log("Invalid max iterations value, defaulting to 10.")
        # Enforce clamp in case of external change
        if max_iters < 0:
            max_iters = 0
        if max_iters > 60:
            max_iters = 60
        
        self.status_label.config(text="Running...", bootstyle=WARNING)
        self.logger.log(f"Starting task with max {max_iters} iterations.")
        self._start_spinner()

        final_code = self.agent.run_task(task, max_iters=max_iters, stream_callback=self.stream_callback)

        # stop spinner
        self._stop_spinner()

        if final_code:
            self.status_label.config(text="Success! ✨", bootstyle=SUCCESS)
            self.logger.log("Task finished successfully.")
        else:
            self.status_label.config(text="Failed to generate a working script. Try a different prompt or more iterations.", bootstyle=DANGER)
            self.logger.log("Task failed. Maximum iterations reached.")
        
        self.run_button.config(state="normal")
        self.example_button.config(state="normal")