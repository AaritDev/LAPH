
import subprocess
import tempfile
import os
import resource

class CodeRunner:
    def run_code(self, code: str):
        """
        Execute Python code in a temporary file with resource limits.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            temp_path = f.name

        def set_limits():
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
