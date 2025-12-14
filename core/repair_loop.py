
import os
import time
from core.llm_interface import LLMInterface
from core.runner import CodeRunner
from core.prompt_manager import PromptManager
from core.logger import Logger

class RepairLoop:
    def __init__(self, logger: Logger, model_name="qwen3:14b"):
        # Load all models
        from core.llm_interface import LLMInterface
        import toml
        models_cfg = toml.load("configs/models.toml")
        self.models = {
            'thinker': LLMInterface(models_cfg['mini']['name']),
            'summariser': LLMInterface(models_cfg['mini']['name']),
            'vision': LLMInterface(models_cfg['vision']['name']),
            'coder': LLMInterface(models_cfg['coder']['name'])
        }
        self.runner = CodeRunner()
        self.prompts = PromptManager()
        self.logger = logger

    def _generate_spec(self, task, code, last_error, stream_callback):
        thinker_prompt = self.prompts.build_thinker(task, code, last_error)
        self.logger.log("--- Thinker Prompt ---\n" + thinker_prompt)
        
        spec = ""
        self.logger.log("--- Thinker Output ---")
        for chunk in self.models['thinker'].generate(thinker_prompt):
            spec += chunk
            if stream_callback:
                stream_callback(chunk, "thinker")
        return spec

    def _generate_code(self, spec, code, last_error, stream_callback):
        coder_prompt = self.prompts.build_coder(spec, code, last_error)
        self.logger.log("--- Coder Prompt ---\n" + coder_prompt)
        
        new_code = ""
        self.logger.log("--- Coder Output ---")
        for chunk in self.models['coder'].generate(coder_prompt):
            new_code += chunk
            if stream_callback:
                stream_callback(chunk, "coder")
        return new_code

    def run_task(self, task: str, max_iters=20, stream_callback=None):
        code = None
        last_error = None

        for i in range(max_iters):
            self.logger.log(f"--- Iteration {i+1}/{max_iters} ---")

            spec = self._generate_spec(task, code, last_error, stream_callback)
            code = self._generate_code(spec, code, last_error, stream_callback)

            self.logger.log("--- Running Code ---")
            stdout, stderr, exitcode = self.runner.run_code(code)

            self.logger.log("--- Execution Result ---")
            self.logger.log("STDOUT:\n" + stdout)
            self.logger.log("STDERR:\n" + stderr)

            if exitcode == 0:
                self.logger.log("🎉 Success! Program runs without errors.")
                return code

            last_error = stderr
            self.logger.log("--- Code failed, trying again... ---")
            time.sleep(2)

        self.logger.log("❌ Failed to generate a working script after max iterations.")
        return None
