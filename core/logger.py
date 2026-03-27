"""Structured logger wrapper around Python logging.

This logger retains a callback mechanism for the UI while adding levels and
rotating file handlers for production readiness.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    """Structured logger with level and callback support."""

    def __init__(self, path="logs/laph.log", level=logging.INFO, max_bytes=5_000_000, backup_count=5):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.callbacks = []

        self.logger = logging.getLogger("laph")
        self.logger.setLevel(level)
        # prevent duplicate handlers when re-creating in tests
        if not self.logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backup_count)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def log(self, message: str, level=logging.INFO):
        if level == logging.DEBUG:
            self.logger.debug(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        else:
            self.logger.info(message)

        framed_message = f"[{logging.getLevelName(level)}] {message}\n"
        for callback in self.callbacks:
            try:
                callback(framed_message)
            except Exception:
                pass

    def clear(self):
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.stream.close()
                handler.baseFilename
        with open(self.logger.handlers[0].baseFilename, "w") as f:
            f.write("")
