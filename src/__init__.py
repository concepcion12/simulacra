"""
Simulacra: Agent-Based Behavioral Simulation

A psychologically-grounded agent-based model that simulates complex human behaviors
including work, housing, addiction, and gambling.
"""

__version__ = "0.1.0"

# Import main classes for convenience
from .agents.agent import Agent
from .simulation.simulation import Simulation
from .environment.city import City

__all__ = [
    "Agent",
    "Simulation", 
    "City",
]
