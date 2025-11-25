class PromptManager:
    def __init__(self, base_path="prompts/base_prompt.txt"):
        with open(base_path, "r") as f:
            self.base_prompt = f.read()

    def build(self, task, code=None, error=None):
        return self.base_prompt.format(
            task=task,
            code=code or "",
            error=error or ""
        )
