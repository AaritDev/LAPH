
import requests
import json

class LLMInterface:
    def __init__(self, model_name="qwen3:14b", temperature: float = 0.0):
        # default to deterministic outputs unless configured otherwise
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str):
        """
        Send a prompt to a local Ollama model via HTTP API and stream the output.
        """
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "temperature": self.temperature
            }
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        full_response += chunk
                        yield chunk
                    except json.JSONDecodeError:
                        # Ignore lines that are not valid JSON
                        pass
        except Exception as e:
            yield f"[LLM ERROR] {e}"
