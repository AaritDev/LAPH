"""Core repair loop orchestration.

This module contains the `RepairLoop` class which coordinates the iterative
Thinker -> Coder -> Runner cycle. It asks the thinker for a specification,
asks the coder to generate code, runs the code in a sandboxed runner, evaluates
output with rich reward signal, and continuously repairs until success or
the maximum iterations are exhausted.
"""

import importlib
import json
import os
import re
import sqlite3
import time
from typing import Callable, Optional, Tuple

from core.llm_interface import LLMInterface
from core.logger import Logger
from core.prompt_manager import PromptManager
from core.runner import CodeRunner


class RepairLoop:
    """Orchestrates the iterative repair cycle with pluggable components."""

    def __init__(self, logger: Optional[Logger] = None, model_name: str = "qwen3:14b") -> None:
        """Initialize LLM interfaces, runner, prompt manager, and plugins."""
        self.logger = logger or Logger()
        self.prompt_manager = PromptManager()

        self.plugins = self._load_plugins()

        # fallback strategies if plugin not available
        self.thinker = self.plugins.get("thinker") or self._default_thinker(model_name)
        self.coder = self.plugins.get("coder") or self._default_coder(model_name)
        self.runner = self.plugins.get("runner") or self._default_runner()
        self.evaluator = self.plugins.get("evaluator") or self._default_evaluator(model_name)

        self.models = {
            "thinker": self.thinker,
            "coder": self.coder,
            "runner": self.runner,
            "evaluator": self.evaluator,
        }

        self.working_code: Optional[str] = None

    def _load_plugins(self) -> dict:
        """Load plugin classes from configs/plugins.toml."""
        try:
            import toml
        except ImportError:
            self.logger.log("toml package not installed; using default built-in plugins", level=30)
            return {}

        plugins = {}
        try:
            cfg = toml.load("configs/plugins.toml")
        except FileNotFoundError:
            return plugins

        for role, section in cfg.items():
            plugin_path = section.get("plugin")
            if not plugin_path:
                continue
            module_name, class_name = plugin_path.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                plugin_class = getattr(module, class_name)
                if role == "thinker":
                    plugins[role] = plugin_class(section.get("model", "qwen3:14b"))
                elif role == "coder":
                    plugins[role] = plugin_class(section.get("model", "qwen2.5-coder:7b-instruct"))
                elif role == "evaluator":
                    plugins[role] = plugin_class(section.get("model", "qwen3:4b"))
                else:
                    plugins[role] = plugin_class()
            except Exception as e:
                self.logger.log(f"[Plugin load failed for {role}] {e}", level=40)

        return plugins

    def _default_thinker(self, model_name: str):
        return self._DefaultThinker(model_name, self.prompt_manager)

    def _default_coder(self, model_name: str):
        return self._DefaultCoder(model_name, self.prompt_manager)

    def _default_runner(self):
        return self._DefaultRunner()

    def _default_evaluator(self, model_name: str):
        return self._DefaultEvaluator(model_name)

    class _DefaultThinker:
        def __init__(self, model_name, prompts):
            self.llm = LLMInterface(model_name)
            self.prompts = prompts

        def generate_spec(self, task, code, error):
            thinker_prompt = self.prompts.build_thinker(task, code, error)
            self_llm_out = ""
            for c in self.llm.generate(thinker_prompt):
                self_llm_out += c
            m = re.search(r"```json\s*([\s\S]*?)```", self_llm_out)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                    return parsed.get("spec", "").strip() if isinstance(parsed, dict) else ""
                except Exception:
                    pass
            m2 = re.search(r"```(?:python\n)?([\s\S]*?)```", self_llm_out)
            if m2:
                return m2.group(1).strip()
            return self_llm_out.strip()

    class _DefaultCoder:
        def __init__(self, model_name, prompts):
            self.llm = LLMInterface(model_name)
            self.prompts = prompts

        def generate_code(self, spec, code, error):
            coder_prompt = self.prompts.build_coder(spec, code, error)
            out = ""
            for c in self.llm.generate(coder_prompt):
                out += c

            fences = re.findall(r"```(?:python\n)?([\s\S]*?)```", out)
            if not fences:
                return out.strip(), None
            if len(fences) == 1:
                return fences[0].strip(), None
            last = fences[-1]
            if "assert " in last or "pytest" in last or "unittest" in last:
                block = "\n\n".join(fences[:-1])
                return block.strip(), last.strip()
            return fences[0].strip(), None

    class _DefaultRunner:
        def __init__(self):
            self.runner = CodeRunner()

        def run(self, code):
            return self.runner.run_code(code)

        def run_code(self, code):
            return self.run(code)

        def run_code_interactive(self, code, inputs=None, timeout=10):
            return self.runner.run_code_interactive(code, inputs=inputs, timeout=timeout)

    class _DefaultEvaluator:
        def __init__(self, model_name):
            self.model_name = model_name
            self.llm = LLMInterface(model_name)

        def evaluate(self, code, stdout, stderr, exitcode, task):
            score = 0.0
            if exitcode == 0:
                score += 1
            if not stderr:
                score += 1
            if stdout.strip():
                score += 1

            query = f"Does this output satisfy the task '{task}'? Output: {stdout}. Answer YES or NO."
            result_str = ""
            for chunk in self.llm.generate(query):
                result_str += chunk

            if "YES" in result_str.upper():
                score += 2
            return score

    def _generate_spec(self, task: str, code: Optional[str], last_error: Optional[str], stream_callback: Optional[Callable[[str, str], None]] = None) -> str:
        return self.thinker.generate_spec(task, code, last_error)

    def _generate_code(self, spec: str, code: Optional[str], last_error: Optional[str], stream_callback: Optional[Callable[[str, str], None]] = None) -> Tuple[str, Optional[str]]:
        return self.coder.generate_code(spec, code, last_error)

    def _split_code_and_tests(self, output: str):
        fences = re.findall(r"```(?:python\n)?([\s\S]*?)```", output)
        if not fences:
            return output, None

        if len(fences) == 1:
            return fences[0], None

        last = fences[-1]
        if "assert " in last or "pytest" in last or "unittest" in last:
            return "\n\n".join(fences[:-1]), last

        return fences[0], None

    def evaluate_output(self, code: str, stdout: str, stderr: str, exitcode: int, task: str) -> float:
        return self.evaluator.evaluate(code, stdout, stderr, exitcode, task)

    def _save_session(self, task: str, code: str, iterations: int, success: bool):
        db = sqlite3.connect("laph.db")
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                task TEXT,
                final_code TEXT,
                iterations INTEGER,
                success INTEGER
            )
            """
        )
        cursor.execute(
            "INSERT INTO sessions VALUES (NULL, datetime('now'), ?, ?, ?, ?)",
            (task, code or "", iterations, int(success)),
        )
        db.commit()
        db.close()

    def _sanitize_code_for_run(self, code: str, tests: Optional[str]) -> Tuple[str, str, Optional[str]]:
        preamble_lines = []
        src = (code or "") + "\n" + (tests or "")

        if (
            ("re." in src or "re.match" in src or "re.search" in src)
            and "import re" not in code
            and "from re" not in code
        ):
            preamble_lines.append("import re")

        if tests and ("random" in src or "randint(" in src):
            if "import random" not in code:
                preamble_lines.append("import random")
            if "randint(" in src and "from random import randint" not in code:
                preamble_lines.append("from random import randint")
            preamble_lines.append("random.seed(0)")
        else:
            if "randint(" in src and "from random import randint" not in code:
                preamble_lines.append("from random import randint")
            elif ("random." in src or "random(" in src) and (
                "import random" not in code and "from random" not in code
            ):
                preamble_lines.append("import random")

        if preamble_lines:
            preamble = "\n".join(preamble_lines) + "\n\n"
            return preamble, code, tests
        return "", code, tests

    def _extract_code_from_output(self, output: str) -> str:
        fence_match = re.search(r"```(?:python\n)?([\s\S]*?)```", output)
        if fence_match:
            return fence_match.group(1).strip()
        fence_match2 = re.search(r"```([\s\S]*?)```", output)
        if fence_match2:
            return fence_match2.group(1).strip()
        return output.strip()

    def run_task(
        self,
        task: str,
        max_iters: int = 20,
        stream_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Optional[str]:
        code = None
        last_error = None
        working_code = None

        for i in range(max_iters):
            self.logger.log(f"--- Iteration {i+1}/{max_iters} ---")

            spec = self.thinker.generate_spec(task, working_code or code, last_error)
            self.logger.log("--- Running Code ---")
            code, tests = self.coder.generate_code(spec, code, last_error)

            run_payload = code
            if tests:
                run_payload = code + "\n\n" + tests

            preamble, run_code_sanitized, run_tests_sanitized = self._sanitize_code_for_run(code, tests)
            if run_tests_sanitized:
                full_payload = preamble + run_code_sanitized + "\n\n" + run_tests_sanitized
            else:
                full_payload = preamble + run_code_sanitized

            self.logger.log("--- Running Code ---")
            stdout, stderr, exitcode = self.runner.run(full_payload)

            self.logger.log("--- Execution Result ---")
            self.logger.log("STDOUT:\n" + stdout)
            self.logger.log("STDERR:\n" + stderr)

            evaluation_score = self.evaluate_output(code, stdout, stderr, exitcode, task)
            self.logger.log(f"Evaluation score: {evaluation_score}")

            if evaluation_score >= 3.0:
                self.logger.log("🎉 Success! Program passes evaluation.")
                working_code = code
                self._save_session(task, code, i + 1, success=True)
                return code

            self.logger.log("--- Invoking Thinker Interaction ---")
            interaction_prompt = self.prompt_manager.build_thinker_interaction(task, code, stdout, stderr, exitcode)
            self.logger.log("--- Thinker Interaction Prompt ---\n" + interaction_prompt)
            if stream_callback:
                stream_callback(interaction_prompt, "thinker_prompt")
                stream_callback(None, "thinker_start")

            interaction_output = ""
            for chunk in self.thinker.llm.generate(interaction_prompt) if hasattr(self.thinker, 'llm') else []:
                interaction_output += chunk
                if stream_callback:
                    stream_callback(chunk, "thinker")

            if stream_callback:
                stream_callback(None, "thinker_end")

            parsed = None
            try:
                m = re.search(r"```json\s*([\s\S]*?)```", interaction_output)
                if m:
                    parsed = json.loads(m.group(1))
                else:
                    start = interaction_output.find("{")
                    end = interaction_output.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        parsed = json.loads(interaction_output[start : end + 1])
            except Exception as e:
                self.logger.log(f"[Thinker interaction parse error] {e}", level=40)

            if isinstance(parsed, dict):
                actions = parsed.get("actions", [])
                followup_spec = parsed.get("followup_spec", "")

                inputs = [a["payload"] for a in actions if a.get("type") == "input"]
                if inputs:
                    self.logger.log("--- Running interactive actions ---")
                    istdout, istderr, iexit = self.runner.run_code_interactive(code, inputs=inputs)
                    self.logger.log("--- Interactive Execution Result ---")
                    self.logger.log("ISTDOUT:\n" + istdout)
                    self.logger.log("ISTDERR:\n" + istderr)
                    last_error = istderr or stderr
                    if followup_spec:
                        self.logger.log("--- Applying followup spec ---")
                        code, tests = self.coder.generate_code(followup_spec, code, last_error)
                        continue
                elif followup_spec:
                    code, tests = self.coder.generate_code(followup_spec, code, last_error)
                    continue

            code = working_code
            last_error = stderr
            self.logger.log("--- Code failed, trying again... ---")
            time.sleep(2)

        self._save_session(task, working_code or "", max_iters, success=False)
        self.logger.log("❌ Failed to generate a working script after max iterations.")
        return None

