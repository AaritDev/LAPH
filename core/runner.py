
"""Sandboxed code execution utilities.

`CodeRunner` executes Python code in temporary files while imposing resource
limits (CPU time and address space) to reduce the risk of runaway executions.
The implementation is intentionally minimal and synchronous for simplicity.
"""

import subprocess
import tempfile
import os
import resource
import time
import shlex
import json

class CodeRunner:
    """Execute and interact with Python code payloads in a temporary sandbox."""
    def run_code(self, code: str):
        """
        Execute Python code in a temporary file with resource limits.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            temp_path = f.name

        def set_limits():
            """Apply resource limits to the child process before execution.

            Limits CPU seconds and address space to reduce the risk of runaway jobs.
            """
            # Limit CPU time to 5 seconds
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            # Limit memory to 256MB
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))

        try:
            result = subprocess.run(
                ["python3", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=8,
                preexec_fn=set_limits
            )
            stdout = result.stdout.decode()
            stderr = result.stderr.decode()
            os.remove(temp_path)
            return stdout, stderr, result.returncode

        except Exception as e:
            os.remove(temp_path)
            return "", f"[Execution Error] {e}", -1

    def run_code_interactive(self, code: str, inputs: list = None, timeout: int = 10):
        """
        Run code and optionally provide a sequence of stdin inputs (sent as one joined string).
        Returns (stdout, stderr, exitcode).
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            temp_path = f.name

        try:
            proc = subprocess.Popen(["python3", temp_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdin_data = None
            if inputs:
                # join inputs with newlines; allow inputs to be strings or dicts
                stdin_data = "\n".join(map(str, inputs)).encode()

            try:
                out, err = proc.communicate(stdin_data, timeout=timeout)
                stdout = out.decode()
                stderr = err.decode()
                return stdout, stderr, proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                return "", "[Interactive Timeout]", -1
        except Exception as e:
            return "", f"[Execution Error] {e}", -1
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
