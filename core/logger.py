import os
import datetime

class Logger:
    def __init__(self, path="logs/laph.log"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        with open(self.path, "a") as f:
            f.write(log_message)
        for callback in self.callbacks:
            callback(log_message)

    def clear(self):
        with open(self.path, "w") as f:
            f.write("")
