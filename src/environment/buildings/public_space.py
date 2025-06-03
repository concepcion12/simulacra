"""
Public space for socializing and begging in Simulacra environment.
"""
from src.environment.buildings.base import Building
from src.utils.types import CueType, FinancialStressCue, PlotID, SubstanceType, BehaviorType, AlcoholCue, GamblingCue

class PublicSpace(Building):
    """Public space where agents can rest, socialize, or beg."""
    def __init__(self, building_id, plot, space_name: str = "public_space"):
        super().__init__(building_id, plot)
        self.space_name = space_name

    def generate_cues(self, agent_location: PlotID):
        """Generate cues in public space (e.g., financial stress cues)."""
        # Public spaces can generate financial stress cues at end of month
        return [FinancialStressCue(intensity=0.5, source=self.plot.id)]

    def can_interact(self, agent) -> bool:
        """Agents can always interact in public spaces."""
        return True

    def __repr__(self) -> str:
        return f"PublicSpace(id={self.id}, name={self.space_name}, plot={self.plot.id})" 