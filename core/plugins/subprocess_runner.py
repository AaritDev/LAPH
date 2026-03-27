from core.plugins.base import RunnerPlugin
from core.runner import CodeRunner


class SubprocessRunner(RunnerPlugin):
    def __init__(self):
        self.runner = CodeRunner()

    def run(self, code: str):
        return self.runner.run_code(code)
