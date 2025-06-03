"""
Residential building and housing unit for Simulacra environment.
"""
from typing import List, Optional
from src.environment.buildings.base import Building
from src.utils.types import UnitID, AgentID

class HousingUnit:
    """Represents a single housing unit within a residential building."""
    def __init__(
        self,
        unit_id: UnitID,
        monthly_rent: float,
        quality: float,  # [0,1]
        occupied_by: Optional[AgentID] = None
    ):
        self.id = unit_id
        self.monthly_rent = monthly_rent
        self.quality = quality
        self.occupied_by = occupied_by

    def get_mood_modifier(self) -> float:
        """Return monthly mood modifier based on quality."""
        return (self.quality - 0.5) * 0.2  # [-0.1, +0.1]

    def get_stress_modifier(self) -> float:
        """Return monthly stress modifier based on quality."""
        return (0.5 - self.quality) * 0.1  # [+0.05, -0.05]

    def is_available(self) -> bool:
        """Check if unit is unoccupied."""
        return self.occupied_by is None

class ResidentialBuilding(Building):
    """Building containing multiple residential units."""
    def __init__(
        self,
        building_id,
        plot,
        units: List[HousingUnit],
        building_quality: float = 0.5
    ):
        super().__init__(building_id, plot)
        self.units = units
        self.building_quality = building_quality

    def get_available_units(self) -> List[HousingUnit]:
        """Return unoccupied housing units."""
        return [u for u in self.units if u.is_available()]

    def get_unit_by_agent(self, agent_id: AgentID) -> Optional[HousingUnit]:
        """Find the unit occupied by the given agent."""
        for u in self.units:
            if u.occupied_by == agent_id:
                return u
        return None

    def generate_cues(self, agent_location: any) -> List:
        """Residential buildings typically do not generate cues."""
        return []

    def can_interact(self, agent) -> bool:
        """Agents can interact if an available unit exists or if they occupy one."""
        if self.get_unit_by_agent(agent.id):
            return True
        return bool(self.get_available_units()) 