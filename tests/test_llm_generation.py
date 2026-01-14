
import pytest
import sys
import os

# Add the project root to sys.path so we can import core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.llm_interface import LLMInterface

def test_llm_simple_code_generation():
    """
    Test that the LLMInterface can connect to the local model and generate code.
    This test requires a local Ollama instance running on port 11434.
    """
    llm = LLMInterface(model_name="qwen2.5:14b", temperature=0.1)
    prompt = "Write a simple Python function named 'add_numbers' that takes two arguments and returns their sum. Only return the code."
    
    print(f"\nSending prompt: {prompt}")
    
    full_response = ""
    try:
        # consume the generator
        for chunk in llm.generate(prompt):
            full_response += chunk
            # print(chunk, end="", flush=True) # Optional: print to stdout to see progress
            
    except Exception as e:
        pytest.fail(f"LLM generation failed (is Ollama running?): {e}")

    print(f"\n\nReceived response:\n{full_response}")

    assert full_response.strip(), "LLM response should not be empty"
    assert "def add_numbers" in full_response, "Response should likely contain the function definition"
    assert "[LLM ERROR]" not in full_response, f"LLM returned an error: {full_response}"

if __name__ == "__main__":
    # Allow running this script directly
    test_llm_simple_code_generation()
