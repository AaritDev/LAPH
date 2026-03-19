"""Lightweight LLM interface for local HTTP-backed models.

This small wrapper sends prompts to a local Ollama-style HTTP API and streams
chunks of text as they arrive. It intentionally yields chunks to support
progressive UI updates.
"""

import requests
import json


class LLMInterface:
    """Send prompts to a local LLM endpoint and yield streamed responses."""

    def __init__(self, model_name="qwen3:14b", temperature: float = 0.0):
        """Create a new interface instance for a named model and temperature."""
        # default to deterministic outputs unless configured otherwise
        self.model_name = model_name
        self.temperature = temperature
        self.last_error: str | None = None

    def generate(self, prompt: str):
        """Send a prompt to a local Ollama model via HTTP API and stream the output."""
        self.last_error = None

        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "temperature": self.temperature,
            }
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()

            try:
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        yield data.get("response", "")
                    except json.JSONDecodeError:
                        # Ignore non-JSON lines
                        continue
            except requests.RequestException as e:
                self.last_error = str(e)
                return
        except Exception as e:
            self.last_error = str(e)
            return
