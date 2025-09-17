"""
Liquor store implementation for Simulacra environment.
"""
from simulacra.environment.buildings.base import Building
from simulacra.utils.types import SubstanceType, AlcoholCue, PlotID


class AlcoholPurchase:
    """Represents an alcohol purchase transaction."""
    def __init__(self, units: int, cost: float):
        self.units = units
        self.cost = cost
        self.substance_type = SubstanceType.ALCOHOL


class LiquorStore(Building):
    """Store where agents can buy alcohol."""
    def __init__(self, building_id, plot, alcohol_price: float = 5.0):
        super().__init__(building_id, plot)
        self.alcohol_price = alcohol_price
        self.cue_base_intensity = 0.6
        self.cue_influence_radius = 2.5

    def sell_alcohol(self, agent, units: int):
        """
        Process an alcohol sale for the agent.
        Returns None if agent cannot afford it.
        """
        cost = units * self.alcohol_price
        if agent.internal_state.wealth < cost:
            return None
        # Deduct money
        agent.internal_state.wealth -= cost
        return AlcoholPurchase(units, cost)

    def generate_cues(self, agent_location: PlotID):
        """Generate alcohol cues based on proximity."""
        # This method is now mainly for backward compatibility
        # The main cue generation is handled by CueGenerator
        return [AlcoholCue(intensity=self.cue_base_intensity, source=self.plot.id)]

    def can_interact(self, agent) -> bool:
        """Can interact if agent has enough wealth."""
        return agent.internal_state.wealth >= self.alcohol_price

    def __repr__(self):
        return (
            f"LiquorStore(id={self.id}, price={self.alcohol_price:.2f}, "
            f"plot={self.plot.id})"
        )
