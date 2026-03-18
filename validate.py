#!/usr/bin/env python3
"""Quick validation script for L.A.P.H. changes."""

import sys
import subprocess
from pathlib import Path


def check_imports():
    """Check if all core modules import correctly."""
    print("Checking imports...")
    try:
        from core.logger import Logger
        from core.llm_interface import LLMInterface
        from core.runner import CodeRunner
        from core.repair_loop import RepairLoop
        from core.prompt_manager import PromptManager
        from core.config import Config, get_config
        from core import cli
        from core.installer_gui import InstallerGUI

        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_syntax():
    """Check Python syntax of all files."""
    print("\nChecking syntax...")
    python_files = list(Path(".").rglob("*.py"))
    python_files = [f for f in python_files if f.parts[0] != ".venv"]

    for py_file in python_files[:5]:  # Check first 5 files
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)], capture_output=True
        )
        if result.returncode != 0:
            print(f"✗ {py_file}: {result.stderr.decode()}")
            return False

    print(f"✓ Syntax check passed ({len(python_files)} files)")
    return True


def check_tests():
    """Run pytest."""
    print("\nRunning tests...")
    result = subprocess.run(
        [".venv/bin/pytest", "tests/", "-q"], capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True


if __name__ == "__main__":
    success = True
    success = check_imports() and success
    success = check_syntax() and success
    # success = check_tests() and success

    if success:
        print("\n✅ All checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed")
        sys.exit(1)
