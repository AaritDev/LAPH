
"""Prompt loader and builders.

This module centralizes the text prompts used to interact with LLM roles
(thinker, coder, summariser, vision). Prompts are loaded from the `prompts/`
directory and small helpers build full prompt strings for each use case.
"""

class PromptManager:
    """Load and format prompts for different LLM roles (thinker, coder, etc.)."""
    def __init__(self):
        """Load prompt templates from the `prompts/` directory into memory."""
        self.prompts = {}
        self.prompts['thinker'] = self._load_prompt('prompts/thinker_prompt.txt')
        self.prompts['thinker_interaction'] = self._load_prompt('prompts/thinker_interaction_prompt.txt')
        self.prompts['summariser'] = self._load_prompt('prompts/summariser_prompt.txt')
        self.prompts['vision'] = self._load_prompt('prompts/vision_prompt.txt')
        self.prompts['coder'] = self._load_prompt('prompts/coder_prompt.txt')

    def _load_prompt(self, path):
        """Read a prompt file from disk and return its contents as a string."""
        with open(path, 'r') as f:
            return f.read()

    def build_thinker(self, task, code=None, error=None):
        """Compose the thinker prompt by inserting task, previous code, and error context."""
        return self.prompts['thinker'] + f"\n\nTask: {task}\n" + (f"Previous code: {code}\n" if code else "") + (f"Error: {error}\n" if error else "")

    def build_thinker_interaction(self, task, code=None, stdout=None, stderr=None, exitcode=None):
        return self.prompts['thinker_interaction'] + f"\n\nTask: {task}\n" + (f"Previous code: {code}\n" if code else "") + (f"STDOUT: {stdout}\n" if stdout is not None else "") + (f"STDERR: {stderr}\n" if stderr is not None else "") + (f"Exitcode: {exitcode}\n" if exitcode is not None else "")

    def build_coder(self, spec, code=None, error=None):
        return self.prompts['coder'] + f"\n\nSpecification: {spec}\n" + (f"Previous code: {code}\n" if code else "") + (f"Error: {error}\n" if error else "")

    def build_summariser(self, logs):
        """Return a summariser prompt with `logs` inserted for context."""
        return self.prompts['summariser'] + f"\n\nLogs: {logs}\n"

    def build_vision(self, description):
        """Return a vision-related prompt with a description inserted."""
        return self.prompts['vision'] + f"\n\nDescription: {description}\n"
