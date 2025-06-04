"""
Building abstract base for Simulacra environment.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from src.utils.types import BuildingID, PlotID, EnvironmentalCue
from src.environment.plot import Plot

if TYPE_CHECKING:
    from src.agents.agent import Agent

class Building(ABC):
    """Abstract base class for all building types."""
    def __init__(self, building_id: BuildingID, plot: Plot):
        self.id = building_id
        self.plot = plot
        # Plot may hold reference to this building
        plot.building = self

    @abstractmethod
    def generate_cues(self, agent_location: PlotID) -> list[EnvironmentalCue]:
        """Generate environmental cues for an agent at a given location."""
        pass

    @abstractmethod
    def can_interact(self, agent: 'Agent') -> bool:
        """Return whether the agent can interact with this building."""
        pass 
