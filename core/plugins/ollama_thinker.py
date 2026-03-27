from core.plugins.base import ThinkerPlugin
from core.llm_interface import LLMInterface
from core.prompt_manager import PromptManager
import re
import json


class OllamaThinker(ThinkerPlugin):
    def __init__(self, model_name: str = "qwen3:14b"):
        self.llm = LLMInterface(model_name)
        self.prompts = PromptManager()

    def generate_spec(self, task: str, code: str = None, error: str = None) -> str:
        prompt = self.prompts.build_thinker(task, code, error)
        output = ""
        for chunk in self.llm.generate(prompt):
            output += chunk

        # Try JSON fenced block first
        m = re.search(r"```json\s*([\s\S]*?)```", output)
        if m:
            try:
                parsed = json.loads(m.group(1))
                return parsed.get("spec", "").strip() if isinstance(parsed, dict) else ""
            except Exception:
                pass

        # fallback to extracting code-like sections
        m2 = re.search(r"```(?:python\n)?([\s\S]*?)```", output)
        if m2:
            return m2.group(1).strip()

        return output.strip()
