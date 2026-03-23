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


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument("task", required=False, nargs=-1)
def cli(ctx, task):
    """L.A.P.H. — Local Autonomous Programming Helper.

    An offline, multi-agent AI system that writes, runs, debugs, and fixes code.

    Quick usage:
        laph "write a hello world program"
        laph generate "task" --max-iterations 20
        laph gui
        laph help
    """
    # Handle special cases that should show help instead of generating code
    if task and len(task) == 1:
        first_arg = task[0].lower()
        if first_arg in ("help", "--help", "-h", "-help"):
            click.echo(ctx.get_help())
            return

    # If a task is provided without a subcommand, treat it as a generate request
    if task and ctx.invoked_subcommand is None:
        ctx.invoke(
            generate,
            task=task,
            max_iterations=10,
            model="qwen3:14b",
            coder_model="qwen2.5-coder:7b-instruct",
            verbose=False,
            output=None,
        )
    elif not ctx.invoked_subcommand and not task:
        # No task and no subcommand -> show help
        click.echo(ctx.get_help())


@cli.command(name="help")
def show_help():
    """Show helpful usage examples and tips."""
    help_text = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  L.A.P.H. — Local Autonomous Programming Helper              ║
║          An offline AI system that writes, runs, debugs, and fixes code      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

📚 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # Generate code from a simple task (easiest way)
  laph "write a hello world program"

  # Use the GUI interface
  laph gui

  # Show this help
  laph help


📋 COMMAND REFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  laph "TASK DESCRIPTION"
    Generate code from natural language (recommended)

  laph generate "TASK" [OPTIONS]
    Generate with advanced options

  laph gui
    Launch graphical user interface

  laph help
    Show this help message

  laph version
    Show version information


⚙️  OPTIONS FOR 'generate' COMMAND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  -i, --max-iterations NUM     Max iterations (1-60, default: 10)
  -m, --model NAME             Thinker model (default: qwen3:14b)
  -c, --coder-model NAME       Coder model (default: qwen2.5-coder:7b)
  -o, --output FILE            Save code to file
  -v, --verbose                Show detailed logs


💡 EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # Simplest usage (recommended)
  laph "write a dice roller with input validation"

  # Save to file
  laph "create a web scraper" -o scraper.py

  # More iterations for complex tasks
  laph generate "build a REST API" --max-iterations 20

  # Custom models
  laph generate "task" --model qwen3:14b --coder-model qwen2.5-coder:7b

  # Verbose output
  laph "task" -v


🔧 ENVIRONMENT VARIABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  LAPH_LLM_ENDPOINT         http://localhost:11434
  LAPH_MODELS_THINKER       qwen3:4b
  LAPH_MODELS_CODER         qwen2.5-coder:7b

Example:
  LAPH_MODELS_CODER=qwen3:7b laph "task"


📖 LINKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GitHub: https://github.com/AaritDev/LAPH

"""
    click.echo(help_text)


@cli.command(context_settings=dict(allow_interspersed_args=False))
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
def version():
    """Show version information."""
    click.echo("L.A.P.H. v0.1.0 — Local Autonomous Programming Helper")
    click.echo("https://github.com/AaritDev/LAPH")


if __name__ == "__main__":
    cli()
