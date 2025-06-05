# Desktop Interface Guide

Simulacra can be launched in a desktop window using PyQt6. This avoids the need for a separate browser window while keeping the full web based interface.

## Installation

Install the optional desktop extras after cloning the repository:

```bash
pip install -e .[desktop]
```

## Launching

Start the desktop UI with the provided console script:

```bash
simulacra-desktop
```

A PyQt window will open and the unified backend will run in the background. Closing the window will automatically stop the server.
