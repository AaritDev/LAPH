from core.plugins.base import CoderPlugin
from core.llm_interface import LLMInterface
from core.prompt_manager import PromptManager
import re


class OllamaCoder(CoderPlugin):
    def __init__(self, model_name: str = "qwen2.5-coder:7b-instruct"):
        self.llm = LLMInterface(model_name)
        self.prompts = PromptManager()

    def generate_code(self, spec: str, code: str = None, error: str = None):
        prompt = self.prompts.build_coder(spec, code, error)
        output = ""
        for chunk in self.llm.generate(prompt):
            output += chunk

        fences = re.findall(r"```(?:python\n)?([\s\S]*?)```", output)
        if not fences:
            return output.strip(), None

        if len(fences) == 1:
            return fences[0].strip(), None

        last = fences[-1]
        if "assert " in last or "pytest" in last or "unittest" in last:
            code_blocks = fences[:-1]
            return "\n\n".join([b.strip() for b in code_blocks]), last.strip()

        return fences[0].strip(), None
