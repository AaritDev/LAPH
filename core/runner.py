import subprocess
import tempfile
import os

class CodeRunner:
    def run_code(self, code: str):
        """
        Execute Python code in a temporary file.
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python3", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=8
            )
            stdout = result.stdout.decode()
            stderr = result.stderr.decode()
            os.remove(temp_path)
            return stdout, stderr, result.returncode

        except Exception as e:
            os.remove(temp_path)
            return "", f"[Execution Error] {e}", -1
