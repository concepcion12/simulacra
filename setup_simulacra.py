"""Cross-platform setup helper for the Simulacra project.

This script creates (or reuses) a virtual environment and installs the
requested optional dependency groups.  It can also bootstrap a conda
environment when ``--use-conda`` is supplied.  The helper replaces the
POSIX-only shell script so new contributors – especially those on
Windows – can prepare the project with a single command:

    python setup_simulacra.py

Run ``python setup_simulacra.py --help`` for the full list of options.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


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
    parser.add_argument(
        "--use-conda",
        action="store_true",
        help=(
            "Create or reuse a conda environment instead of using python -m venv."
            " Requires the conda command to be available."
        ),
    )
    parser.add_argument(
        "--conda-env",
        default="simulacra",
        help=(
            "Name of the conda environment to manage when --use-conda is provided."
            " (default: simulacra)"
        ),
    )
    parser.add_argument(
        "--conda-python",
        default="3.10",
        help=(
            "Python version to install when creating a conda environment."
            " (default: 3.10)"
        ),
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


def conda_available() -> bool:
    return shutil.which("conda") is not None


def ensure_conda_available() -> None:
    if not conda_available():
        raise SystemExit(
            "The 'conda' command was not found. Install Miniconda/Anaconda or "
            "run without --use-conda."
        )


def conda_env_exists(env_name: str) -> bool:
    try:
        output = subprocess.check_output(
            ["conda", "env", "list", "--json"], text=True
        )
        envs = json.loads(output).get("envs", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise SystemExit("Unable to query conda environments.") from error

    for env_path in envs:
        path = Path(env_path)
        if path.name == env_name or path == Path(env_name):
            return True
    return False


def remove_conda_env(env_name: str) -> None:
    subprocess.check_call(["conda", "env", "remove", "--yes", "--name", env_name])


def create_conda_env(env_name: str, python_version: str) -> None:
    print(
        f"Creating conda environment '{env_name}' with Python {python_version} …"
    )
    subprocess.check_call(
        ["conda", "create", "--yes", "--name", env_name, f"python={python_version}"]
    )


def conda_python_path(env_name: str) -> Path:
    python_location = subprocess.check_output(
        [
            "conda",
            "run",
            "-n",
            env_name,
            "python",
            "-c",
            "import sys; print(sys.executable)",
        ],
        text=True,
    ).strip()
    path = Path(python_location)
    if not path.exists():
        raise SystemExit(
            f"Unable to locate python executable for conda environment '{env_name}'."
        )
    return path


def ensure_conda_python_version(env_name: str) -> Tuple[int, int]:
    version = subprocess.check_output(
        [
            "conda",
            "run",
            "-n",
            env_name,
            "python",
            "-c",
            "import sys; print('.'.join(map(str, sys.version_info[:2])))",
        ],
        text=True,
    ).strip()
    try:
        major_str, minor_str = version.split(".")[:2]
        major, minor = int(major_str), int(minor_str)
    except ValueError as error:
        raise SystemExit(
            f"Unexpected Python version string for conda env '{env_name}': {version}"
        ) from error
    if (major, minor) < (3, 10):
        raise SystemExit(
            "Simulacra requires Python >= 3.10. The conda environment "
            f"'{env_name}' is using {version}. Run with --force-recreate to rebuild it "
            "with a newer Python interpreter."
        )
    return major, minor


def prepare_conda_environment(
    env_name: str, python_version: str, force_recreate: bool
) -> Path:
    if force_recreate and conda_env_exists(env_name):
        print(f"Removing existing conda environment '{env_name}'")
        remove_conda_env(env_name)

    if conda_env_exists(env_name):
        print(f"Reusing conda environment '{env_name}'")
    else:
        create_conda_env(env_name, python_version)

    major, minor = ensure_conda_python_version(env_name)
    print(f"Conda environment Python version: {major}.{minor}")
    return conda_python_path(env_name)


def warn_about_active_environment(
    use_conda: bool, target_conda_env: Optional[str]
) -> None:
    if os.environ.get("VIRTUAL_ENV"):
        if use_conda:
            print(
                "ℹ️  Detected an active virtual environment. Conda will create its "
                "own environment. Run 'deactivate' first if you prefer a clean "
                "shell."
            )
        else:
            print(
                "ℹ️  Detected an active virtual environment. The helper ignores it "
                "and manages the environment requested here."
            )

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        active_name = os.environ.get("CONDA_DEFAULT_ENV", conda_prefix)
        if use_conda:
            if target_conda_env and active_name == target_conda_env:
                print(
                    f"ℹ️  Conda environment '{active_name}' is already active."
                    " Dependencies will be installed in place."
                )
            else:
                hint = target_conda_env or "the target environment"
                print(
                    f"ℹ️  Detected active conda environment '{active_name}'. The "
                    f"helper will install into {hint}."
                )
        else:
            print(
                f"ℹ️  Detected active conda environment '{active_name}'. Pass "
                "--use-conda to install dependencies inside conda instead of a "
                ".venv."
            )


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


def venv_activation_instructions(venv_path: Path) -> str:
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


def conda_activation_instructions(env_name: str) -> str:
    return (
        f"Activate the environment in any shell with: `conda activate {env_name}`"
    )


def main() -> None:
    args = parse_args()

    if args.use_conda:
        ensure_conda_available()
    else:
        ensure_python_version()

    root = project_root()
    os.chdir(root)

    warn_about_active_environment(args.use_conda, args.conda_env if args.use_conda else None)

    extras = normalize_extras(args.extras, args.include_dev)

    if args.use_conda:
        python_path = prepare_conda_environment(
            args.conda_env, args.conda_python, args.force_recreate
        )
        activation_hint = conda_activation_instructions(args.conda_env)
    else:
        venv_arg = Path(args.venv)
        venv_path = (
            venv_arg if venv_arg.is_absolute() else (root / venv_arg).resolve()
        )
        if args.force_recreate:
            print(f"Removing existing virtual environment at {venv_path}")
            recreate_venv(venv_path)

        create_venv(venv_path)
        python_path = venv_python(venv_path)
        activation_hint = venv_activation_instructions(
            venv_arg if not venv_arg.is_absolute() else venv_path
        )

    install_dependencies(python_path, extras)

    print("\n✅ Simulacra environment ready.")
    print("To activate the environment run:")
    print(activation_hint)
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
