# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-15

### Added

- Initial MVP release
- Core agent loop: Thinker → Coder → Runner → Iterate
- Support for Qwen2.5-Coder (7B) and Qwen3 (14B) models
- CLI with Click framework
- GUI installer with progress tracking
- Sandboxed code execution with resource limits (5s CPU, 256MB RAM)
- Type hints throughout codebase
- Comprehensive test suite (80%+ coverage)
- Documentation: README, CONTRIBUTING, ARCHITECTURE guides

### Fixed

- Tempfile resource leak in `core/runner.py`
- Spinner race condition in `core/gui.py`
- Parser type checking for JSON responses in `core/repair_loop.py`
- Streaming error handling in `core/llm_interface.py`
- Platform-specific resource limit handling (Windows compatibility)

### Changed

- Unified random import logic in sanitizer
- Improved error messages in all modules
- Updated themes and UI colors for better readability

### Removed

- Dead code in CLI (unused TOML loading)
- Duplicate help function consolidation

## [Unreleased]

### Planned

- Phase 2: Vision feedback loop with screenshot analysis
- Multi-model dynamic routing
- Auto-dependency installation
- Session history storage in SQLite
- Export functionality with metadata
- Internationalization (i18n) support
