"""One-time setup script for KAIROS-HEDGE."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Run complete first-time setup."""
    print("=" * 60)
    print("  KAIROS-HEDGE — First-Time Setup")
    print("=" * 60)

    _check_python_version()
    _create_venv()
    _install_requirements()
    _create_output_dirs()
    _create_env_file()
    _print_next_steps()


def _check_python_version() -> None:
    """Verify Python 3.11+ is installed."""
    print("\n[1/5] Checking Python version...")
    major, minor = sys.version_info[:2]
    if major < 3 or minor < 11:
        print(f"  ERROR: Python 3.11+ required, found {major}.{minor}")
        print("  Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"  ✅ Python {major}.{minor} detected")


def _create_venv() -> None:
    """Create virtual environment if it doesn't exist."""
    print("\n[2/5] Creating virtual environment...")
    venv_path = Path("venv")
    if venv_path.exists():
        print("  ✅ venv already exists")
        return
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("  ✅ venv created")


def _install_requirements() -> None:
    """Install all dependencies into the virtual environment."""
    print("\n[3/5] Installing dependencies...")
    pip_path = _get_pip_path()
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    print("  ✅ All dependencies installed")


def _create_output_dirs() -> None:
    """Create output directories."""
    print("\n[4/5] Creating output directories...")
    dirs = [
        Path("output"),
        Path("output/reports"),
        Path("output/logs"),
        Path("credentials"),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  ✅ Output directories created")


def _create_env_file() -> None:
    """Copy .env.example to .env if not exists."""
    print("\n[5/5] Setting up .env file...")
    env_path = Path(".env")
    example_path = Path(".env.example")
    if env_path.exists():
        print("  ✅ .env already exists")
        return
    if example_path.exists():
        shutil.copy(example_path, env_path)
        print("  ✅ .env created from .env.example")
        print("  ⚠️  IMPORTANT: Edit .env and fill in your API keys!")
    else:
        print("  ⚠️  .env.example not found — create .env manually")


def _get_pip_path() -> Path:
    """Get the pip executable path for the venv."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    return Path("venv/bin/pip")


def _print_next_steps() -> None:
    """Print post-setup instructions."""
    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("  Next steps:")
    print("  1. Edit .env and fill in your API keys")
    print("     - Groq: https://console.groq.com")
    print("     - Gemini: https://aistudio.google.com")
    print("     - OpenRouter: https://openrouter.ai")
    print("     - Telegram: Search @BotFather on Telegram")
    print()
    print("  2. (Optional) Adjust thresholds in config.yaml")
    print()
    print("  3. Run every Sunday:")
    if platform.system() == "Windows":
        print("     Double-click run_sunday.bat")
        print("     OR: venv\\Scripts\\activate && python run_weekly.py")
    else:
        print("     ./run_sunday.sh")
        print("     OR: source venv/bin/activate && python run_weekly.py")
    print()


if __name__ == "__main__":
    main()
