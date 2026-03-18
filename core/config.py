"""Configuration management for L.A.P.H.

Supports configuration from:
1. Environment variables (LAPH_*)
2. Config files (~/.config/laph/config.yaml)
3. Built-in defaults
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager with environment variable and file support."""

    DEFAULTS = {
        "llm": {
            "endpoint": "http://localhost:11434",
            "timeout": 30,
            "retries": 3,
        },
        "models": {
            "thinker": "qwen3:4b",
            "coder": "qwen2.5-coder:7b-instruct",
            "vision": "qwen3-vl:8b",
        },
        "sandbox": {
            "cpu_limit_seconds": 5,
            "memory_limit_mb": 256,
            "timeout_seconds": 8,
        },
        "repair": {
            "max_iterations": 20,
            "max_iterations_limit": 60,
        },
    }

    def __init__(self):
        """Initialize configuration from defaults, files, and environment."""
        self.config: Dict[str, Any] = {}
        self._load_defaults()
        self._load_from_file()
        self._load_from_env()

    def _load_defaults(self):
        """Load default configuration."""
        self.config = {
            k: dict(v) if isinstance(v, dict) else v for k, v in self.DEFAULTS.items()
        }

    def _load_from_file(self):
        """Load configuration from ~/.config/laph/config.yaml if it exists."""
        config_path = Path.home() / ".config" / "laph" / "config.yaml"
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    file_config = yaml.safe_load(f) or {}
                self._merge_config(self.config, file_config)
            except ImportError:
                pass  # YAML optional
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables (LAPH_* prefix)."""
        for key, value in os.environ.items():
            if key.startswith("LAPH_"):
                # Parse LAPH_SECTION_KEY=value format
                parts = key[5:].lower().split("_", 1)
                if len(parts) == 2:
                    section, subkey = parts
                    if section not in self.config:
                        self.config[section] = {}
                    # Try to parse as int/bool/float if possible
                    parsed_value: Any = value
                    if value.lower() in ("true", "false"):
                        parsed_value = value.lower() == "true"
                    elif value.isdigit():
                        parsed_value = int(value)
                    elif value.replace(".", "", 1).isdigit():
                        parsed_value = float(value)
                    self.config[section][subkey] = parsed_value

    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value in section.key format."""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        if default is not None:
            return default
        # Return default from DEFAULTS if available
        if section in self.DEFAULTS and key in self.DEFAULTS[section]:
            return self.DEFAULTS[section][key]
        return None

    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def llm_endpoint(self) -> str:
        """Get LLM API endpoint."""
        return self.get("llm", "endpoint", "http://localhost:11434")

    def llm_timeout(self) -> int:
        """Get LLM API timeout in seconds."""
        return self.get("llm", "timeout", 30)

    def thinker_model(self) -> str:
        """Get thinker model name."""
        return self.get("models", "thinker", "qwen3:4b")

    def coder_model(self) -> str:
        """Get coder model name."""
        return self.get("models", "coder", "qwen2.5-coder:7b-instruct")

    def vision_model(self) -> str:
        """Get vision model name."""
        return self.get("models", "vision", "qwen3-vl:8b")

    def max_iterations(self) -> int:
        """Get default max repair iterations."""
        max_iters = self.get("repair", "max_iterations", 10)
        max_limit = self.get("repair", "max_iterations_limit", 60)
        return min(max(max_iters, 1), max_limit)

    def cpu_limit_seconds(self) -> int:
        """Get sandbox CPU limit in seconds."""
        return self.get("sandbox", "cpu_limit_seconds", 5)

    def memory_limit_mb(self) -> int:
        """Get sandbox memory limit in MB."""
        return self.get("sandbox", "memory_limit_mb", 256)

    def sandbox_timeout(self) -> int:
        """Get sandbox timeout in seconds."""
        return self.get("sandbox", "timeout_seconds", 8)


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config_instance
    _config_instance = None
