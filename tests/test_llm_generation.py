import json
import os
import sys

import pytest

# Add the project root to sys.path so we can import core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from core.llm_interface import LLMInterface


def test_llm_simple_code_generation(monkeypatch):
    """Ensure the LLM interface streams model output correctly.

    This test mocks the HTTP response so it does not require a running Ollama
    instance.
    """

    def fake_post(url, **kwargs):
        class FakeResponse:
            def raise_for_status(self):
                return None

            def iter_lines(self):
                # Simulate streamed JSON response lines from Ollama
                yield json.dumps(
                    {"response": "def add_numbers(a, b):\n    return a + b\n"}
                ).encode()

        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    llm = LLMInterface(model_name="qwen2.5:14b", temperature=0.1)
    prompt = "Write a simple Python function named 'add_numbers' that takes two arguments and returns their sum. Only return the code."

    full_response = ""
    for chunk in llm.generate(prompt):
        full_response += chunk

    assert full_response.strip(), "LLM response should not be empty"
    assert (
        "def add_numbers" in full_response
    ), "Response should likely contain the function definition"
    assert "[LLM ERROR]" not in full_response, f"LLM returned an error: {full_response}"


if __name__ == "__main__":
    # Allow running this script directly
    test_llm_simple_code_generation()
