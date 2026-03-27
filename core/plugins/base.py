from abc import ABC, abstractmethod
from typing import Tuple, Optional


class ThinkerPlugin(ABC):
    @abstractmethod
    def generate_spec(self, task: str, code: Optional[str], error: Optional[str]) -> str:
        pass


class CoderPlugin(ABC):
    @abstractmethod
    def generate_code(self, spec: str, code: Optional[str], error: Optional[str]) -> Tuple[str, Optional[str]]:
        pass


class RunnerPlugin(ABC):
    @abstractmethod
    def run(self, code: str) -> Tuple[str, str, int]:
        pass


class EvaluatorPlugin(ABC):
    @abstractmethod
    def evaluate(self, code: str, stdout: str, stderr: str, exitcode: int, task: str) -> float:
        pass
