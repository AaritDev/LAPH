# Copyright (C) 2025 L.A.P.H. Contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of L.A.P.H. (Local Autonomous Programming Helper)
# See LICENSE for details.

"""Global constants for L.A.P.H."""

# ─────────────────────────────────────────────────────────────────────────
# GUI Dimensions
# ─────────────────────────────────────────────────────────────────────────

GUI_WIDTH: int = 1400
GUI_HEIGHT: int = 900
HEADER_HEIGHT: int = 96
SIDEBAR_WIDTH: int = 250

# ─────────────────────────────────────────────────────────────────────────
# Sandbox & Execution Limits
# ─────────────────────────────────────────────────────────────────────────

CPU_LIMIT_SECONDS: int = 5
MEMORY_LIMIT_MB: int = 256
EXECUTION_TIMEOUT_SECONDS: int = 8

# ─────────────────────────────────────────────────────────────────────────
# Iteration Limits
# ─────────────────────────────────────────────────────────────────────────

MIN_ITERATIONS: int = 1
MAX_ITERATIONS: int = 60
DEFAULT_ITERATIONS: int = 10

# ─────────────────────────────────────────────────────────────────────────
# Model Defaults
# ─────────────────────────────────────────────────────────────────────────

DEFAULT_THINKER_MODEL: str = "qwen3:14b"
DEFAULT_CODER_MODEL: str = "qwen2.5-coder:7b-instruct"
DEFAULT_VISION_MODEL: str = "qwen3-vl:8b"
DEFAULT_SUMMARIZER_MODEL: str = "qwen3:4b"

# ─────────────────────────────────────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────────────────────────────────────

OLLAMA_ENDPOINT: str = "http://localhost:11434"
DEFAULT_TEMPERATURE: float = 0.7
STREAMING_ENABLED: bool = True

# ─────────────────────────────────────────────────────────────────────────
# Rate Limiting
# ─────────────────────────────────────────────────────────────────────────

MAX_LLM_CALLS_PER_TASK: int = 100
REQUEST_TIMEOUT_SECONDS: int = 300

# ─────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────

LOG_LEVEL: str = "INFO"
LOG_DIR: str = "logs"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ─────────────────────────────────────────────────────────────────────────
# Error Codes
# ─────────────────────────────────────────────────────────────────────────

ERROR_CONNECTION_FAILED: str = "LAPH_E001"
ERROR_MODEL_NOT_FOUND: str = "LAPH_E002"
ERROR_TIMEOUT: str = "LAPH_E003"
ERROR_INVALID_INPUT: str = "LAPH_E004"
ERROR_EXECUTION_FAILED: str = "LAPH_E005"
