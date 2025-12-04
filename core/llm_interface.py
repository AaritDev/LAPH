
import requests

class LLMInterface:
    def __init__(self, model_name="qwen3:14b"):
        self.model_name = model_name

    def generate(self, prompt: str):
        """
        Send a prompt to a local Ollama model via HTTP API and return the output.
        """
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "[No response]")
        except Exception as e:
            return f"[LLM ERROR] {e}"
