# Simulacra

Simulacra is an agent-based urban simulation platform focused on behavioral economics, addiction dynamics and real-time visualization. It provides tools to create populations, run city-scale simulations and analyze results with a rich analytics system.

## Features

- **Agent architecture** with decision making based on behavioral economics principles
- **Environment and building system** for cities with districts and spatial cues
- **Population generation** utilities for realistic or custom agent distributions
- **Analytics** module collecting detailed agent and population metrics
- **Real-time dashboard** and web-based setup wizard built with Flask and Socket.IO

## Installation

```bash
pip install -r requirements.txt
```

Optional dashboard requirements:

```bash
pip install flask flask-socketio gevent gevent-websocket
```

## Quick Start

Launch the unified interface with the setup wizard and dashboard:

```bash
python start_unified_interface.py
```

Open <http://localhost:5000> in your browser to configure and run a simulation.

### Running the Example Scripts

Demo scripts are located in the `examples/` directory. Run them from the project
root so the `src` package can be discovered:

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
