"""Command-line interface for L.A.P.H. using click.

Provides a user-friendly CLI for running code generation tasks without the GUI.
"""

import click
import sys
from pathlib import Path
from core.repair_loop import RepairLoop
from core.logger import Logger


class CLILogger(Logger):
    """Logger that prints to stdout for CLI usage."""

    def __init__(self, verbose: bool = False):
        """Initialize CLI logger without file persistence."""
        self.callbacks = []
        self.verbose = verbose

    def log(self, message: str):
        """Print message to stdout."""
        if self.verbose or "---" in message or "🎉" in message or "❌" in message:
            click.echo(message)


def stream_to_cli(chunk: str | None, source: str):
    """Stream callback for CLI output.

    Displays streaming output from models in real-time.
    """
    if chunk is None:
        return

    # Only show important milestones and generated code/output
    if source in ("coder", "thinker"):
        click.echo(chunk, nl=False)
    elif source == "coder_end":
        click.echo("\n" + "-" * 60)
    elif source == "thinker_end":
        click.echo("\n" + "-" * 60)


@click.group()
def cli():
    """L.A.P.H. — Local Autonomous Programming Helper.

    An offline, multi-agent AI system that writes, runs, debugs, and fixes code.
    """
    pass


@cli.command()
@click.argument("task", required=True, nargs=-1)
@click.option(
    "--max-iterations",
    "-i",
    type=int,
    default=10,
    help="Maximum repair loop iterations (default: 10, max: 60).",
)
@click.option(
    "--model",
    "-m",
    type=str,
    default="qwen3:14b",
    help="Thinker model to use (default: qwen3:14b).",
)
@click.option(
    "--coder-model",
    "-c",
    type=str,
    default="qwen2.5-coder:7b-instruct",
    help="Coder model to use (default: qwen2.5-coder:7b-instruct).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose output including all logs.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Write generated code to a file.",
)
def generate(
    task: tuple,
    max_iterations: int,
    model: str,
    coder_model: str,
    verbose: bool,
    output: str | None,
):
    """Generate code from a task description.

    Example:
        laph generate "write a dice roller with input validation"
    """
    task_str = " ".join(task)

    if not task_str:
        click.echo(click.style("Error: Task description required.", fg="red"), err=True)
        sys.exit(1)

    if max_iterations < 1 or max_iterations > 60:
        click.echo(
            click.style("Error: Max iterations must be between 1 and 60.", fg="red"),
            err=True,
        )
        sys.exit(1)

    click.echo(
        click.style(f"\n🚀 Starting L.A.P.H. Code Generation", fg="cyan", bold=True)
    )
    click.echo(f"Task: {task_str}")
    click.echo(f"Max iterations: {max_iterations}")
    click.echo(f"Models: Thinker={model}, Coder={coder_model}\n")

    logger = CLILogger(verbose=verbose)
    agent = RepairLoop(logger, model_name=model)
    # Override the coder model if specified
    from core.llm_interface import LLMInterface
    import toml

    models_cfg = toml.load("configs/models.toml")
    agent.models["coder"] = LLMInterface(coder_model)

    try:
        click.echo(click.style("Generating specification...", fg="yellow", bold=True))
        final_code = agent.run_task(
            task_str, max_iters=max_iterations, stream_callback=stream_to_cli
        )

        if final_code:
            click.echo(
                click.style("\n✨ Success! Generated code:\n", fg="green", bold=True)
            )
            click.echo(final_code)

            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(final_code)
                click.echo(click.style(f"\n✅ Code written to: {output}", fg="green"))
        else:
            click.echo(
                click.style(
                    "\n❌ Failed to generate code after max iterations.",
                    fg="red",
                    bold=True,
                ),
                err=True,
            )
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo(click.style("\n⚠️ Interrupted by user.", fg="yellow"), err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red", bold=True), err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
def gui():
    """Launch the graphical user interface."""
    try:
        import tkinter as tk
        from core.gui import LAPH_GUI

        click.echo(click.style("Launching L.A.P.H. GUI...", fg="cyan"))
        root = tk.Tk()
        app = LAPH_GUI(root)
        root.mainloop()
    except ImportError as e:
        click.echo(
            click.style(f"Error: Missing dependency for GUI: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)


@cli.command()
def install():
    """Launch the installer GUI."""
    try:
        from core.installer_gui import run_installer_gui

        run_installer_gui()
    except ImportError as e:
        click.echo(
            click.style(f"Error: Missing dependency for installer: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("L.A.P.H. v0.1.0 — Local Autonomous Programming Helper")
    click.echo("https://github.com/AaritDev/LAPH")


if __name__ == "__main__":
    cli()
