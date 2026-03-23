"""GUI installer for L.A.P.H. — Interactive installation wizard.

Provides a user-friendly installation experience with progress tracking
and configuration options.
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER, INFO, WARNING
from ttkbootstrap.widgets import ToolTip


def perform_install(
    install_root,
    create_desktop=True,
    download_models=False,
    source_dir=None,
    log_callback=None,
    progress_callback=None,
):
    """Perform the installation steps (shared GUI + CLI)."""
    install_root = Path(install_root).expanduser().resolve()
    if source_dir is None:
        source_dir = Path(__file__).parent.parent
    else:
        source_dir = Path(source_dir).expanduser().resolve()

    app_dir = install_root / "bin" / "LAPH"
    venv_dir = app_dir / "venv"
    desktop_dir = install_root / "share" / "applications"
    icon_dir = install_root / "share" / "icons" / "hicolor" / "256x256" / "apps"

    def report(message):
        if log_callback:
            log_callback(message)

    def progress(value, status):
        if progress_callback:
            progress_callback(value, status)

    report(f"📁 Creating installation directories at {app_dir}...")
    progress(5, "Creating directories...")

    app_dir.mkdir(parents=True, exist_ok=True)
    desktop_dir.mkdir(parents=True, exist_ok=True)
    icon_dir.mkdir(parents=True, exist_ok=True)
    report(f"✓ Directories created at {app_dir}")

    report("📦 Copying project files...")
    progress(20, "Copying project files...")

    import shutil

    for item in source_dir.iterdir():
        if item.name in (
            ".git",
            ".venv",
            "venv",
            "logs",
            "__pycache__",
            ".pytest_cache",
        ):
            continue
        dest = app_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    report("✓ Project files copied")

    report("🐍 Creating Python virtual environment...")
    progress(35, "Creating virtual environment...")
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        capture_output=True,
    )
    report("✓ Virtual environment created")

    report("📚 Installing Python dependencies...")
    progress(50, "Installing dependencies...")

    pip_exe = venv_dir / "bin" / "pip"
    reqs_file = app_dir / "requirements.txt"
    if reqs_file.exists():
        subprocess.run(
            [str(pip_exe), "install", "-q", "-r", str(reqs_file)],
            check=True,
            capture_output=True,
        )
    report("✓ Dependencies installed")

    report("⚙️ Creating launcher scripts...")
    progress(70, "Creating launcher scripts...")

    bin_dir = install_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launcher_path = app_dir / "laph"
    launcher_path.write_text(f"""#!/usr/bin/env bash
set -e
HERE=\"$(cd \"$(dirname \"$0\")\" && pwd)\"
\"$HERE/venv/bin/python\" \"$HERE/main.py\" gui \"$@\"
""")
    launcher_path.chmod(0o755)

    symlink_path = bin_dir / "laph"
    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()
    symlink_path.symlink_to(launcher_path)
    report(f"✓ Launcher created at {symlink_path}")

    cli_launcher = app_dir / "laph-cli"
    cli_launcher.write_text(f"""#!/usr/bin/env bash
set -e
HERE=\"$(cd \"$(dirname \"$0\")\" && pwd)\"
\"$HERE/venv/bin/python\" "-m" "core.cli" "$@"
""")
    cli_launcher.chmod(0o755)

    cli_symlink = bin_dir / "laph-cli"
    if cli_symlink.exists() or cli_symlink.is_symlink():
        cli_symlink.unlink()
    cli_symlink.symlink_to(cli_launcher)
    report(f"✓ CLI launcher created at {cli_symlink}")

    if create_desktop:
        report("🖥️ Configuring desktop entry...")
        progress(80, "Configuring desktop entry...")
        desktop_file = desktop_dir / "laph.desktop"
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=L.A.P.H.
Comment=Local Autonomous Programming Helper
Exec=\"{launcher_path}\" %u
Terminal=false
Categories=Development;Utility;
StartupNotify=true
Keywords=code;generation;ai;programming;
"""
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o644)
        report(f"✓ Desktop entry created at {desktop_file}")
        try:
            subprocess.run(
                ["update-desktop-database", str(desktop_dir)],
                capture_output=True,
                timeout=5,
            )
            report("✓ Desktop database updated")
        except Exception:
            report("⚠️ Could not update desktop database (optional)")

    if download_models:
        report("🤖 Pulling Ollama models (this may take a few minutes)...")
        progress(90, "Downloading models...")
        try:
            subprocess.run(
                ["ollama", "pull", "qwen2.5-coder:7b-instruct"],
                check=True,
                timeout=600,
            )
            subprocess.run(
                ["ollama", "pull", "qwen3:14b"],
                check=True,
                timeout=600,
            )
            report("✓ Models downloaded successfully")
        except FileNotFoundError:
            report("⚠️ Ollama not found. Please install it manually.")
        except Exception as e:
            report(f"⚠️ Could not pull models: {e}")

    progress(100, "Installation complete")
    report("✅ Installation successful!")
    report(f"   Installed to: {app_dir}")
    report("   Run 'laph' or 'laph-cli' from your terminal")
    return {
        "app_dir": str(app_dir),
        "launcher": str(symlink_path),
        "cli_launcher": str(cli_symlink),
    }


class InstallerGUI:
    """Interactive installer GUI for L.A.P.H."""

    def __init__(self, root):
        """Initialize the installer window."""
        self.root = root
        self.root.title("L.A.P.H. Installer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Apply theme
        style = tb.Style("cosmo")

        # installation paths
        self.install_root = Path.home() / ".local"
        self.install_root_var = tk.StringVar(value=str(self.install_root))
        self.app_dir = self.install_root / "bin" / "LAPH"
        self.venv_dir = self.app_dir / "venv"
        self.desktop_dir = self.install_root / "share" / "applications"
        self.icon_dir = (
            self.install_root / "share" / "icons" / "hicolor" / "256x256" / "apps"
        )

        self.setup_ui()

    def setup_ui(self):
        """Create and layout all UI widgets."""
        main_frame = tb.Frame(self.root, padding=20, bootstyle="light")
        main_frame.pack(fill="both", expand=True)

        # Header
        header = tb.Label(
            main_frame,
            text="L.A.P.H. Installation Wizard",
            font=("Arial", 18, "bold"),
            bootstyle="inverse-primary",
        )
        header.pack(fill="x", pady=(0, 10))

        # Description
        self.desc = tb.Label(
            main_frame,
            text="Local Autonomous Programming Helper\nApplication directory: " + str(self.app_dir),
            font=("Arial", 10),
            bootstyle="info",
            justify="center",
        )
        self.desc.pack(fill="x", pady=(0, 20))

        # Installation path
        path_frame = tb.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 10))

        tb.Label(path_frame, text="Install root:", bootstyle="secondary").pack(side="left")
        self.install_path_entry = tb.Entry(path_frame, textvariable=self.install_root_var, bootstyle="info")
        self.install_path_entry.pack(side="left", fill="x", expand=True, padx=5)

        browse_btn = tb.Button(path_frame, text="Browse", command=self.choose_install_path, bootstyle="info")
        browse_btn.pack(side="right")

        # Options frame
        options_frame = tb.Labelframe(
            main_frame, text="Installation Options", padding=15, bootstyle="info"
        )
        options_frame.pack(fill="x", pady=(0, 15))

        # Desktop entry checkbox
        self.desktop_var = tk.BooleanVar(value=True)
        desktop_check = tb.Checkbutton(
            options_frame,
            text="Create desktop launcher",
            variable=self.desktop_var,
            bootstyle="info",
        )
        desktop_check.pack(anchor="w", pady=5)
        ToolTip(desktop_check, text="Create a desktop shortcut for easy access")

        # Pull models checkbox
        self.models_var = tk.BooleanVar(value=False)
        models_check = tb.Checkbutton(
            options_frame,
            text="Download LLM models (requires Ollama & internet)",
            variable=self.models_var,
            bootstyle="info",
        )
        models_check.pack(anchor="w", pady=5)
        ToolTip(models_check, text="Download recommended AI models (may take time)")

        # Progress
        progress_frame = tb.Frame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_label = tb.Label(
            progress_frame, text="Ready to install", bootstyle="info"
        )
        self.progress_label.pack(anchor="w")

        self.progress = tb.Progressbar(
            progress_frame, mode="determinate", bootstyle="info", length=400
        )
        self.progress.pack(fill="x", pady=(5, 0))

        # Buttons
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 0))

        self.launch_btn = tb.Button(
            button_frame,
            text="Launch Now",
            command=self.launch_app,
            bootstyle=INFO,
            width=12,
            state="disabled",
        )
        self.launch_btn.pack(side="left", padx=5)
        ToolTip(self.launch_btn, text="Launch the installed L.A.P.H. application")

        self.install_btn = tb.Button(
            button_frame,
            text="Install",
            command=self.start_install,
            bootstyle=SUCCESS,
            width=12,
        )
        self.install_btn.pack(side="right", padx=5)
        ToolTip(self.install_btn, text="Start the installation process")

        cancel_btn = tb.Button(
            button_frame,
            text="Cancel",
            command=self.root.quit,
            bootstyle=DANGER,
            width=12,
        )
        cancel_btn.pack(side="right", padx=5)
        ToolTip(cancel_btn, text="Exit the installer")

        # Log area
        log_frame = tb.Labelframe(
            main_frame, text="Installation Log", padding=10, bootstyle="light"
        )
        log_frame.pack(fill="both", expand=True, pady=(15, 0))

        self.log_text = tk.Text(
            log_frame,
            height=8,
            width=70,
            font=("Courier", 9),
            bg="#f8f9fa",
            fg="#212529",
            insertbackground="#212529",
            borderwidth=0,
            relief="flat",
        )
        self.log_text.pack(fill="both", expand=True)

        scrollbar = tb.Scrollbar(
            log_frame, command=self.log_text.yview, bootstyle="info"
        )
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def choose_install_path(self):
        """Open folder picker for install root."""
        selected = filedialog.askdirectory(initialdir=str(self.install_root))
        if selected:
            self.install_root_var.set(selected)
            self.update_paths()

    def update_paths(self):
        """Update installation paths when user changes install root."""
        self.install_root = Path(self.install_root_var.get()).expanduser().resolve()
        self.app_dir = self.install_root / "bin" / "LAPH"
        self.venv_dir = self.app_dir / "venv"
        self.desktop_dir = self.install_root / "share" / "applications"
        self.icon_dir = (
            self.install_root / "share" / "icons" / "hicolor" / "256x256" / "apps"
        )
        self.desc.config(
            text="Local Autonomous Programming Helper\nApplication directory: "
            + str(self.app_dir)
        )

    def log_message(self, message: str):
        """Append a message to the log area."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def start_install(self):
        """Start installation in a background thread."""
        self.install_btn.config(state="disabled")
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        """Execute the installation steps using shared installer logic."""

        def progress_callback(value, status):
            self.progress["value"] = value
            self.progress_label.config(text=status)

        try:
            self.log_text.delete("1.0", tk.END)
            self.progress["value"] = 0
            self.progress_label.config(text="Starting installation...")

            self.update_paths()

            perform_install(
                install_root=self.install_root,
                create_desktop=self.desktop_var.get(),
                download_models=self.models_var.get(),
                source_dir=Path(__file__).parent.parent,
                log_callback=self.log_message,
                progress_callback=progress_callback,
            )

            self.progress["value"] = 100
            self.progress_label.config(text="Installation complete!")
            self.log_message("")
            self.log_message("✅ Installation successful!")
            self.log_message(f"   Installed to: {self.app_dir}")
            self.log_message("   Run 'laph' or 'laph-cli' from your terminal")

            messagebox.showinfo(
                "Installation Complete",
                f"L.A.P.H. installed successfully!\n\n"
                f"Location: {self.app_dir}\n\n"
                f"Run 'laph' to launch the GUI\n"
                f"Run 'laph-cli' for the command-line interface",
            )

            self.install_btn.config(state="disabled")
            self.launch_btn.config(state="normal")

        except Exception as e:
            self.log_message(f"❌ Installation failed: {e}")
            messagebox.showerror("Installation Failed", f"Error during installation:\n{e}")
            self.install_btn.config(state="normal")
            self.launch_btn.config(state="disabled")

            # Create launcher script
            bin_dir = self.install_root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            launcher_path = self.app_dir / "laph"
            launcher_path.write_text(f"""#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
"$HERE/venv/bin/python" "$HERE/main.py" gui "$@"
""")
            launcher_path.chmod(0o755)

            # Create symlink
            symlink_path = bin_dir / "laph"
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
            symlink_path.symlink_to(launcher_path)
            self.log_message(f"✓ Launcher created at {symlink_path}")

            # Create CLI symlink
            cli_symlink = bin_dir / "laph-cli"
            if cli_symlink.exists() or cli_symlink.is_symlink():
                cli_symlink.unlink()
            cli_launcher = self.app_dir / "laph-cli"
            cli_launcher.write_text(f"""#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
"$HERE/venv/bin/python" "-m" "core.cli" "$@"
""")
            cli_launcher.chmod(0o755)
            cli_symlink.symlink_to(cli_launcher)
            self.log_message(f"✓ CLI launcher created at {cli_symlink}")

            self.progress["value"] = 75
            self.progress_label.config(text="Configuring desktop...")
            self.log_message("🖥️ Configuring desktop entry...")

            if self.desktop_var.get():
                desktop_file = self.desktop_dir / "laph.desktop"
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=L.A.P.H.
Comment=Local Autonomous Programming Helper
Exec="{launcher_path}" %u
Terminal=false
Categories=Development;Utility;
StartupNotify=true
Keywords=code;generation;ai;programming;
"""
                desktop_file.write_text(desktop_content)
                desktop_file.chmod(0o644)
                self.log_message(f"✓ Desktop entry created at {desktop_file}")

                # Update desktop database
                try:
                    subprocess.run(
                        ["update-desktop-database", str(self.desktop_dir)],
                        capture_output=True,
                        timeout=5,
                    )
                    self.log_message("✓ Desktop database updated")
                except Exception:
                    self.log_message("⚠️ Could not update desktop database (optional)")

            self.progress["value"] = 85
            self.progress_label.config(text="Downloading models (optional)...")

            if self.models_var.get():
                self.log_message(
                    "🤖 Pulling Ollama models (this may take a few minutes)..."
                )
                try:
                    subprocess.run(
                        ["ollama", "pull", "qwen2.5-coder:7b-instruct"],
                        check=True,
                        timeout=600,
                    )
                    subprocess.run(
                        ["ollama", "pull", "qwen3:14b"],
                        check=True,
                        timeout=600,
                    )
                    self.log_message("✓ Models downloaded successfully")
                except FileNotFoundError:
                    self.log_message("⚠️ Ollama not found. Please install it manually.")
                except Exception as e:
                    self.log_message(f"⚠️ Could not pull models: {e}")

            self.progress["value"] = 100
            self.progress_label.config(text="Installation complete!")
            self.log_message("")
            self.log_message("✅ Installation successful!")
            self.log_message(f"   Installed to: {self.app_dir}")
            self.log_message(f"   Run 'laph' or 'laph-cli' from your terminal")
            self.log_message("")

            messagebox.showinfo(
                "Installation Complete",
                f"L.A.P.H. installed successfully!\n\n"
                f"Location: {self.app_dir}\n\n"
                f"Run 'laph' to launch the GUI\n"
                f"Run 'laph-cli' for the command-line interface",
            )

            self.install_btn.config(state="disabled")
            self.launch_btn.config(state="normal")

            # self.root.quit()  # Removed to allow launching

        except Exception as e:
            self.log_message(f"❌ Installation failed: {e}")
            messagebox.showerror(
                "Installation Failed", f"Error during installation:\n{e}"
            )
            self.install_btn.config(state="normal")
            self.launch_btn.config(state="disabled")


    def launch_app(self):
        """Launch the installed application."""
        launcher_path = self.app_dir / "laph"
        try:
            subprocess.Popen([str(launcher_path)])
            self.log_message("🚀 Launching L.A.P.H....")
            self.root.quit()  # Close installer after launching
        except Exception as e:
            messagebox.showerror("Launch Failed", f"Could not launch app: {e}")


def run_installer_gui():
    """Launch the installer GUI."""
    root = tb.Window(themename="cosmo")
    installer = InstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_installer_gui()
