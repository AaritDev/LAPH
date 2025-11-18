from core.llm_interface import LLMInterface
from core.runner import CodeRunner
from core.prompt_manager import PromptManager
from core.logger import Logger

class RepairLoop:
    def __init__(self, model_name="qwen3:14b"):
        self.llm = LLMInterface(model_name)
        self.runner = CodeRunner()
        self.prompts = PromptManager()
        self.logger = Logger()

    def run_task(self, task: str, max_iters=10):
        code = None
        last_error = None

        for i in range(max_iters):
            prompt = self.prompts.build(task, code, last_error)
            code = self.llm.generate(prompt)

            self.logger.log(f"=== Iteration {i+1} ===")
            self.logger.log("Generated code:\n" + code)

            stdout, stderr, exitcode = self.runner.run_code(code)

            self.logger.log("STDOUT:\n" + stdout)
            self.logger.log("STDERR:\n" + stderr)

            if exitcode == 0:
                print("🎉 Success! Program runs without errors.")
                return code

            last_error = stderr

        print("❌ Failed after max iterations.")
        return None
