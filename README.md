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

The easiest way to get started is to run the provided setup script which creates
a virtual environment and installs all optional extras:

```bash
./setup_simulacra.sh
```

If you prefer manual installation, install the package in editable mode using the provided `pyproject.toml`:

```bash
pip install -e .
```

Optional visualization extras can be installed with:

```bash
pip install .[visualization]
```

For the desktop launcher, install the additional PyQt packages:

```bash
pip install .[desktop]
```

## Quick Start

Launch the unified interface with the setup wizard and dashboard:

```bash
python start_unified_interface.py
```

Open <http://localhost:5000> in your browser to configure and run a simulation.

Alternatively, you can launch a desktop window that embeds the interface so no
external browser is required. After installing the `desktop` extras, run:

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

Detailed guides and additional documentation are located in the `docs/` directory. Start with `docs/README.md` for an in‑depth overview of available features.
