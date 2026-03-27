from core.plugins.base import EvaluatorPlugin


class ExitCodeEvaluator(EvaluatorPlugin):
    def evaluate(self, code: str, stdout: str, stderr: str, exitcode: int, task: str) -> float:
        score = 0.0
        if exitcode == 0:
            score = 5.0
        return score
