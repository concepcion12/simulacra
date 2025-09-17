# Simulacra Installation & Setup Guide

This guide expands on the README quickstart and walks through a dependable
installation flow for every platform, with a special focus on Windows users.

## 1. Install the prerequisites

| Requirement | Notes |
| --- | --- |
| Python 3.10+ | Download from [python.org](https://www.python.org/downloads/) and tick **Add Python to PATH** during installation. |
| `pip` | Comes with Python. The setup helper upgrades it automatically. |
| Git | Optional but recommended so you can pull updates easily. |
| Visual C++ Build Tools (Windows) | Needed only if you build native packages. Install from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/). |

> 💡 **Check your Python installation**
>
> - Windows (PowerShell): `py --version`
> - macOS/Linux: `python3 --version`
>
> If the command is not found, reinstall Python and ensure it is on your PATH.

## 2. Clone the repository

```bash
git clone https://github.com/<your-org>/simulacra.git
cd simulacra
```

If you downloaded a zip archive instead, extract it and open a terminal in the
project folder.

## 3. Run the bootstrap helper

Launch the cross-platform setup script. It creates a `.venv` directory by
default, upgrades `pip`, installs the default optional extras (`desktop` and
`visualization`), and prints clear activation instructions tailored to your
shell. The helper refuses to proceed if it detects an unsupported Python
version and warns if another environment is already active, so you always know
what it is about to modify.

| Platform | Command |
| --- | --- |
| Windows (PowerShell) | `py setup_simulacra.py` |
| Windows (Command Prompt) | `python setup_simulacra.py` |
| macOS / Linux | `python3 setup_simulacra.py` |
| Any platform (manage everything inside conda) | `python setup_simulacra.py --use-conda` |

Commonly used flags:

- `--force-recreate`: delete and rebuild the virtual environment if it already exists.
- `--extras visualization`: install only selected extras (space separated list).
- `--include-dev`: add linting, testing and documentation tooling.
- `--conda-env simulacra`: pick a custom environment name when using conda.
- `--conda-python 3.11`: create the conda environment with a specific Python
  version (defaults to 3.10).

Run `python setup_simulacra.py --help` to see every option.

> 🟦 **Prefer a conda workflow?**
>
> The helper automates conda just as well:
>
> ```bash
> python setup_simulacra.py --use-conda --conda-env simulacra
> ```
>
> This creates (or reuses) the named environment, ensures it runs Python 3.10+
> and installs the requested extras. When the script finishes, activate it with
> `conda activate simulacra` and you are ready to go.

## 4. Activate the virtual environment

| Shell | Activation command |
| --- | --- |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.\.venv\Scripts\activate.bat` |
| Windows Git Bash / WSL | `source .venv/bin/activate` |
| macOS / Linux | `source .venv/bin/activate` |

If PowerShell blocks the script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This change applies only to the current shell session.

## 5. Verify the installation

With the environment activated, run the smoke test:

```bash
python -c "import simulacra; print('Simulacra is ready!')"
```

You can also launch the setup wizard immediately:

```bash
python start_unified_interface.py
```

Then open <http://localhost:5000> in your browser.

## Manual installation fallback

If you prefer to manage the environment yourself:

```bash
python -m venv .venv
source .venv/bin/activate  # or Windows equivalent
python -m pip install --upgrade pip
python -m pip install -e .[desktop,visualization]
```

For conda users:

```bash
conda create --name simulacra python=3.10
conda activate simulacra
python -m pip install --upgrade pip
python -m pip install -e .[desktop,visualization]
```

You can omit the extras (`.[desktop,visualization]`) or replace them with any
subset (for example `.[visualization]`).

## Troubleshooting tips

- **“python is not recognized” (Windows)** – reopen your terminal after
  installation or reinstall Python and tick “Add Python to PATH”.
- **PowerShell execution policy errors** – run the one-line command shown in
  step 4 or execute the activation script from Command Prompt instead.
- **Proxy/firewall issues** – pre-download the dependencies by running
  `python -m pip download -r requirements.txt` while online and point `pip` to
  that directory using `--find-links` when offline.
- **M1/M2 macOS dependency issues** – ensure you are using the arm64 Python
  build from python.org. If you must use Rosetta, create the environment with
  `arch -x86_64 python3 setup_simulacra.py`.

Still stuck? Open an issue with your OS version, Python version, and the exact
error message so we can help.
