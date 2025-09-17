"""Cross-platform setup helper for the Simulacra project.

This script creates (or reuses) a virtual environment and installs the
requested optional dependency groups.  It is intended to replace the
POSIX-only shell script so new contributors – especially those on
Windows – can prepare the project with a single command:

    python setup_simulacra.py

Run ``python setup_simulacra.py --help`` for the full list of options.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a virtual environment and install Simulacra with the"
            " selected extras."
        )
    )
    parser.add_argument(
        "--venv",
        default=".venv",
        help="Directory where the virtual environment should live (default: .venv)",
    )
    parser.add_argument(
        "--extras",
        nargs="*",
        default=["desktop", "visualization"],
        help=(
            "Optional dependency groups to install (default: desktop visualization)."
            " Pass nothing to skip extras entirely."
        ),
    )
    parser.add_argument(
        "--include-dev",
        action="store_true",
        help="Install the dev tooling extra in addition to the requested extras.",
    )
    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="Delete any existing virtual environment before creating a new one.",
    )
    return parser.parse_args()


def ensure_python_version() -> None:
    required_major, required_minor = 3, 10
    if sys.version_info < (required_major, required_minor):
        raise SystemExit(
            "Simulacra requires Python >= 3.10. "
            f"Detected {platform.python_version()}"
        )


def project_root() -> Path:
    root = Path(__file__).resolve().parent
    if not (root / "pyproject.toml").is_file():
        raise SystemExit(
            "Unable to locate pyproject.toml. Please run this script from the"
            " Simulacra repository."
        )
    return root


def recreate_venv(venv_path: Path) -> None:
    if venv_path.exists():
        shutil.rmtree(venv_path)


def create_venv(venv_path: Path) -> None:
    if venv_path.exists():
        print(f"Reusing existing virtual environment at {venv_path}")
        return
    print(f"Creating virtual environment at {venv_path} …")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])


def venv_python(venv_path: Path) -> Path:
    scripts_dir = "Scripts" if platform.system() == "Windows" else "bin"
    python_name = "python.exe" if platform.system() == "Windows" else "python"
    python_path = venv_path / scripts_dir / python_name
    if not python_path.exists():
        raise SystemExit(
            f"Python executable not found inside {venv_path}. "
            "Try running with --force-recreate."
        )
    return python_path


def normalize_extras(extras: Iterable[str], include_dev: bool) -> List[str]:
    selected = [extra.strip() for extra in extras if extra.strip()]
    if include_dev:
        selected.append("dev")
    # Preserve order but remove duplicates.
    seen: set[str] = set()
    ordered: List[str] = []
    for extra in selected:
        if extra not in seen:
            ordered.append(extra)
            seen.add(extra)
    return ordered


def install_dependencies(python_path: Path, extras: List[str]) -> None:
    def run_step(description: str, command: List[str]) -> None:
        print(f"\n→ {description}")
        subprocess.check_call([str(python_path), *command])

    run_step("Upgrading pip", ["-m", "pip", "install", "--upgrade", "pip"])

    if extras:
        target = f".[{','.join(extras)}]"
        friendly = ", ".join(extras)
        print(f"Installing Simulacra with extras: {friendly}")
    else:
        target = "."
        print("Installing Simulacra without optional extras")

    run_step("Installing project dependencies", ["-m", "pip", "install", "-e", target])


def activation_instructions(venv_path: Path) -> str:
    """Return a human-friendly activation hint for the virtual environment."""

    if platform.system() == "Windows":
        ps_path = Path(venv_path) / "Scripts" / "Activate.ps1"
        cmd_path = Path(venv_path) / "Scripts" / "activate.bat"
        prefix = "" if Path(venv_path).is_absolute() else f".{os.sep}"
        return (
            f"Windows PowerShell: `{prefix}{ps_path}`\n"
            f"Windows Command Prompt: `{prefix}{cmd_path}`"
        )

    activate_path = Path(venv_path) / "bin" / "activate"
    return f"Unix/macOS shell: `source {activate_path}`"


def main() -> None:
    ensure_python_version()
    args = parse_args()

    root = project_root()
    os.chdir(root)

    venv_arg = Path(args.venv)
    venv_path = venv_arg if venv_arg.is_absolute() else (root / venv_arg).resolve()
    if args.force_recreate:
        print(f"Removing existing virtual environment at {venv_path}")
        recreate_venv(venv_path)

    create_venv(venv_path)
    python_path = venv_python(venv_path)

    extras = normalize_extras(args.extras, args.include_dev)
    install_dependencies(python_path, extras)

    print("\n✅ Simulacra environment ready.")
    print("To activate the virtual environment run:")
    print(activation_instructions(venv_arg if not venv_arg.is_absolute() else venv_path))
    print(
        "\nNext steps:\n"
        "  1. Activate the environment.\n"
        "  2. Launch the unified interface with `python start_unified_interface.py`.\n"
        "  3. Open http://localhost:5000 in your browser."
    )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Command failed with exit code {error.returncode}.") from error
