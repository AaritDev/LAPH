"""Sandboxed code execution utilities.

`CodeRunner` executes Python code in temporary files while imposing resource
limits (CPU time and address space) to reduce the risk of runaway executions.
The implementation is intentionally minimal and synchronous for simplicity.
"""

import subprocess
import sys
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
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as f:
                f.write(code)
                temp_path = f.name
            if os.name == 'posix':
                os.chmod(temp_path, 0o600)

            def set_limits():
                """Apply resource limits to the child process before execution.

                Limits CPU seconds and address space to reduce the risk of runaway jobs.
                """
                if os.name == 'posix':  # Unix-like systems only
                    # Limit CPU time to 5 seconds
                    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
                    # Limit memory to 256MB
                    resource.setrlimit(
                        resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024)
                    )

            result = subprocess.run(
                [sys.executable, temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=8,
                preexec_fn=set_limits if os.name == 'posix' else None,
            )
            stdout = result.stdout.decode()
            stderr = result.stderr.decode()
            return stdout, stderr, result.returncode

        except Exception as e:
            return "", f"[Execution Error] {e}", -1
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass  # Ignore if file already deleted or inaccessible

    def run_code_interactive(self, code: str, inputs: list = None, timeout: int = 10):
        """
        Run code and optionally provide a sequence of stdin inputs (sent as one joined string).
        Returns (stdout, stderr, exitcode).
        """
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as f:
                f.write(code)
                temp_path = f.name
            if os.name == 'posix':
                os.chmod(temp_path, 0o600)

            proc = subprocess.Popen(
                [sys.executable, temp_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

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
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
