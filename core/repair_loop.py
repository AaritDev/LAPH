
import os
import time
from core.llm_interface import LLMInterface
from core.runner import CodeRunner
from core.prompt_manager import PromptManager
from core.logger import Logger
import json

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
        # Separate code and optional tests from fenced blocks
        code_piece, tests_piece = self._split_code_and_tests(new_code)
        cleaned = code_piece.strip()
        return cleaned, tests_piece

    def _split_code_and_tests(self, output: str):
        """Return (code, tests) where tests is a string or None."""
        import re
        fences = re.findall(r"```(?:python\n)?([\s\S]*?)```", output)
        if not fences:
            # no fenced blocks; everything is code
            return output, None
        if len(fences) == 1:
            # single fenced block: assume it's code
            return fences[0], None
        # multiple fenced blocks: heuristically pick the last as tests if it contains 'assert' or 'pytest'
        last = fences[-1]
        if 'assert ' in last or 'pytest' in last or 'unittest' in last:
            # code is everything before the last fence extracted
            code_blocks = fences[:-1]
            return "\n\n".join(code_blocks), last
        # otherwise assume first block is code
        return fences[0], None

    def _extract_code_from_output(self, output: str) -> str:
        # If the model wrapped code in ``` fences, extract the first fenced block.
        import re
        fence_match = re.search(r"```(?:python\n)?([\s\S]*?)```", output)
        if fence_match:
            return fence_match.group(1).strip()
        # Sometimes models include triple grave accents with no language
        fence_match2 = re.search(r"```([\s\S]*?)```", output)
        if fence_match2:
            return fence_match2.group(1).strip()
        # Otherwise, assume all output is code; but strip any leading explanatory lines
        return output.strip()

    def run_task(self, task: str, max_iters=20, stream_callback=None):
        code = None
        last_error = None

        for i in range(max_iters):
            self.logger.log(f"--- Iteration {i+1}/{max_iters} ---")

            spec = self._generate_spec(task, code, last_error, stream_callback)
            self.logger.log("--- Running Code ---")
            code, tests = self._generate_code(spec, code, last_error, stream_callback)

            # If tests are present, append them to the code so they run together
            run_payload = code
            if tests:
                run_payload = code + "\n\n" + tests

            self.logger.log("--- Running Code ---")
            stdout, stderr, exitcode = self.runner.run_code(run_payload)

            self.logger.log("--- Execution Result ---")
            self.logger.log("STDOUT:\n" + stdout)
            self.logger.log("STDERR:\n" + stderr)

            if exitcode == 0:
                self.logger.log("🎉 Success! Program runs without errors.")
                return code

            # Give the Thinker a chance to interact with the failed run and gather more evidence
            self.logger.log("--- Invoking Thinker Interaction ---")
            interaction_prompt = self.prompts.build_thinker_interaction(task, code, stdout, stderr, exitcode)
            self.logger.log("--- Thinker Interaction Prompt ---\n" + interaction_prompt)

            interaction_output = ""
            for chunk in self.models['thinker'].generate(interaction_prompt):
                interaction_output += chunk
                if stream_callback:
                    stream_callback(chunk, "thinker")

            # Try to parse JSON out of the thinker's output
            parsed = None
            try:
                start = interaction_output.find('{')
                end = interaction_output.rfind('}')
                if start != -1 and end != -1 and end > start:
                    parsed = json.loads(interaction_output[start:end+1])
            except Exception as e:
                self.logger.log(f"[Thinker parse error] {e}")

            if parsed:
                actions = parsed.get('actions', [])
                followup_spec = parsed.get('followup_spec', '')

                # Execute any input actions
                inputs = [a['payload'] for a in actions if a.get('type') == 'input']
                if inputs:
                    self.logger.log("--- Running interactive actions ---")
                    istdout, istderr, iexit = self.runner.run_code_interactive(code, inputs=inputs)
                    self.logger.log("--- Interactive Execution Result ---")
                    self.logger.log("ISTDOUT:\n" + istdout)
                    self.logger.log("ISTDERR:\n" + istderr)
                    # After interactions, feed results back into thinker/coder cycle as last_error
                    last_error = istderr or stderr
                    # Optionally push a new spec to coder if available
                    if followup_spec:
                        spec = followup_spec
                        # generate a new code attempt with the followup spec
                        code = self._generate_code(spec, code, last_error, stream_callback)
                        continue
                else:
                    # No input actions; if a followup_spec exists, use it
                    if followup_spec:
                        spec = followup_spec
                        code = self._generate_code(spec, code, last_error, stream_callback)
                        continue

            # Fallback: no usable interaction or followup, set last_error and retry with same loop
            last_error = stderr
            self.logger.log("--- Code failed, trying again... ---")
            time.sleep(2)

        self.logger.log("❌ Failed to generate a working script after max iterations.")
        return None
