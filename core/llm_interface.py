import subprocess
import json

class LLMInterface:
    def __init__(self, model_name="qwen3:14b"):
        self.model_name = model_name

    def generate(self, prompt: str):
        """
        Send a prompt to a local Ollama model and return the output.
        """
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode().strip()

        except Exception as e:
            return f"[LLM ERROR] {e}"
