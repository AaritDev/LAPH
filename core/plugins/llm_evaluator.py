from core.plugins.base import EvaluatorPlugin
from core.llm_interface import LLMInterface


class LLMEvaluator(EvaluatorPlugin):
    def __init__(self, model_name: str = "qwen3:4b"):
        self.llm = LLMInterface(model_name)

    def evaluate(self, code: str, stdout: str, stderr: str, exitcode: int, task: str) -> float:
        score = 0.0
        if exitcode == 0:
            score += 1.0
        if not stderr:
            score += 1.0
        if stdout.strip():
            score += 1.0

        query = (
            f"Does this output satisfy the task '{task}'? Output: {stdout}. "
            "Answer YES or NO."
        )
        output = ""
        for chunk in self.llm.generate(query):
            output += chunk

        if "YES" in output.upper():
            score += 2.0

        return score
