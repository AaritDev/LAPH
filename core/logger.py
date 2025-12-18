"""Simple file-backed logger with callback hooks.

This logger writes timestamped messages to a file and optionally notifies
registered callbacks (e.g., a UI log window) so they can react to log events.
"""

import os
import datetime

class Logger:
    """Logger that appends timestamped messages to a logfile and notifies callbacks."""

    def __init__(self, path="logs/laph.log"):
        """Prepare the log file's containing directory and initialize callback list."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.callbacks = []

    def register_callback(self, callback):
        """Register a callable to be invoked with each log message (string)."""
        self.callbacks.append(callback)

    def log(self, message: str):
        """Append a timestamped message to the log file and notify callbacks."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        with open(self.path, "a") as f:
            f.write(log_message)
        for callback in self.callbacks:
            callback(log_message)

    def clear(self):
        """Clear the log file contents (truncate to zero)."""
        with open(self.path, "w") as f:
            f.write("")
