"""Tests for the repair loop orchestration and sandboxed runner.

These tests exercise parsing of fenced code and JSON, interactive runner inputs,
and the behavior of the repair loop when models yield particular outputs.
"""

import json
import time
from core.repair_loop import RepairLoop
from core.runner import CodeRunner


def test_extract_code_from_fence():
    rl = RepairLoop(None)
    out = "Some text\n```python\nprint(\"hello\")\n```\nTrailing"
    extracted = rl._extract_code_from_output(out)
    assert "print(\"hello\")" in extracted


def test_run_code_interactive_inputs():
    runner = CodeRunner()
    code = 's = input()\nprint("GOT:", s)'
    stdout, stderr, code_ret = runner.run_code_interactive(code, inputs=["abc"])
    assert "GOT: abc" in stdout


def test_split_code_and_tests():
    rl = RepairLoop(None)
    out = "```python\nprint('a')\n```\nSome text\n```\nassert 1 == 1\n```"
    code, tests = rl._split_code_and_tests(out)
    assert "print('a')" in code
    assert "assert 1 == 1" in tests


class FakeModel:
    def __init__(self, outputs):
        self.outputs = outputs

    def generate(self, prompt):
        for o in self.outputs:
            yield o


def test_repair_loop_interaction_cycle():
    # Create a RepairLoop with fake thinker and coder models
    class DummyLogger:
        def log(self, *args, **kwargs):
            pass
    rl = RepairLoop(DummyLogger())
    # Replace real models with fakes
    # First thinker generates a simple spec
    rl.models['thinker'] = FakeModel(["Create a program that echoes the input."])
    # First coder produces code that will error (NameError)
    bad_code = "```python\nprint(unknown_var)\n```"
    rl.models['coder'] = FakeModel([bad_code, "```python\nprint('fixed')\n```"])

    # Thinker interaction after error: instruct to input 'hello' and give followup to fix
    interaction_json = '{"actions": [{"type": "input", "payload": "hello"}], "followup_spec": "Replace unknown_var with input()"}'
    rl.models['thinker'] = FakeModel([interaction_json])

    # Run a single iteration of the loop: we expect it to try, fail, invoke thinker, attempt followup
    code = None
    last_error = None
    spec = rl._generate_spec('echo', code, last_error, None)
    code, tests = rl._generate_code(spec, code, last_error, None)
    # Running the bad code should error
    stdout, stderr, exitcode = rl.runner.run_code(code)
    assert exitcode != 0
    # Now interaction
    interaction_prompt = rl.prompts.build_thinker_interaction('echo', code, stdout, stderr, exitcode)
    out = ''.join(list(rl.models['thinker'].generate(interaction_prompt)))
    parsed = None
    start = out.find('{')
    end = out.rfind('}')
    if start != -1 and end != -1:
        parsed = json.loads(out[start:end+1])
    assert parsed
    assert parsed['actions'][0]['payload'] == 'hello'


def test_generate_spec_parses_fenced_json():
    rl = RepairLoop(None)
    # Thinker returns a fenced JSON block with spec key
    rl.models['thinker'] = FakeModel(["```json\n{\"spec\": \"Do the thing\"}\n```\n"])
    spec = rl._generate_spec('task', None, None, None)
    assert spec == 'Do the thing'