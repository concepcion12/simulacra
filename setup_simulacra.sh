#!/usr/bin/env bash
# Simple setup script for Simulacra
# Creates a virtual environment and installs required dependencies.
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[desktop,visualization]
echo "\nSimulacra environment ready. Activate with 'source .venv/bin/activate'"
