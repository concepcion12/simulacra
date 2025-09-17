# Simulacra

Simulacra is an agent-based urban simulation platform focused on behavioral economics, addiction dynamics and real-time visualization. It provides tools to create populations, run city-scale simulations and analyze results with a rich analytics system.

## Features

- **Agent architecture** with decision making based on behavioral economics principles
- **Environment and building system** for cities with districts and spatial cues
- **Population generation** utilities for realistic or custom agent distributions
- **Analytics** module collecting detailed agent and population metrics
- **Real-time dashboard** and web-based setup wizard built with Flask and Socket.IO
- **Threaded simulation** option for faster agent updates
- **Pause/resume controls** to manage running simulations

## Installation

### 1. Requirements

- Python 3.10 or newer (verify with `python --version` or `py --version` on Windows)
- `pip` 22+ (automatically upgraded by the setup helper)
- Git for cloning the repository
- **Windows only:** we recommend installing Python from [python.org](https://www.python.org/downloads/) with the “Add Python to PATH” option enabled. If you plan to build native extensions, also install the [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### 2. One-command bootstrap (recommended)

Run the cross-platform helper to create a `.venv` directory and install Simulacra with the visualization and desktop extras.

| Platform | Command |
| --- | --- |
| Windows (PowerShell) | `py setup_simulacra.py` |
| Windows (Command Prompt) | `python setup_simulacra.py` |
| macOS / Linux | `python3 setup_simulacra.py` |

The script accepts optional flags such as `--force-recreate` to rebuild the virtual environment, `--extras` to customise installed extras, and `--include-dev` to pull in linting/test tooling. Run `python setup_simulacra.py --help` for the complete list.

### 3. Activate the virtual environment

| Shell | Command |
| --- | --- |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.\.venv\Scripts\activate.bat` |
| macOS / Linux (bash/zsh/fish via bash compatibility) | `source .venv/bin/activate` |

If PowerShell blocks the activation script, temporarily enable it with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

### 4. Verify the installation

After activation, run the quick smoke test:

```bash
python -c "import simulacra; print('Simulacra is ready!')"
```

You should see `Simulacra is ready!` without any import errors.

### Manual installation (alternative)

If you cannot run the helper script, create a virtual environment manually and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate  # or the Windows equivalent above
python -m pip install --upgrade pip
python -m pip install -e .[desktop,visualization]
```

The legacy `setup_simulacra.sh` wrapper simply invokes `python3 setup_simulacra.py` for convenience on POSIX systems.

## Quick Start

Launch the unified interface with the setup wizard and dashboard:

```bash
python start_unified_interface.py
```

Open <http://localhost:5000> in your browser to configure and run a simulation.

Alternatively, you can launch a desktop window that embeds the interface so no
external browser is required. After installing the `desktop` extras (included by default
when using `setup_simulacra.py`), run:

```bash
simulacra-desktop
```

### Running the Example Scripts

Demo scripts are located in the `examples/` directory. Install the project in
editable mode so the `simulacra` package is importable, then run for example:

```bash
python examples/cue_system_demo.py
```

## Running Tests

This project uses `pytest`. To execute the test suite run:

```bash
pytest
```

## Documentation

Detailed guides and additional documentation are located in the `docs/` directory. Start with `docs/README.md` for an in‑depth overview of available features and see `docs/SETUP.md` for the step-by-step installation guide.
