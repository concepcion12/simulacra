"""
Casino building and associated games for Simulacra environment.
"""
import random
from typing import List
from src.environment.buildings.base import Building
from src.utils.types import (
    PlotID, GamblingOutcome, GamblingCue
)


class GamblingGame:
    """Represents a gambling game with probabilities and payouts."""
    def __init__(
        self,
        name: str,
        min_bet: float,
        max_bet: float,
        base_win_probability: float,
        payout_ratio: float,
        near_miss_probability: float = 0.05
    ):
        self.name = name
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.base_win_probability = base_win_probability
        self.payout_ratio = payout_ratio
        self.near_miss_probability = near_miss_probability

    def play(self, bet: float) -> GamblingOutcome:
        """Simulate playing the game with a given bet."""
        roll = random.random()
        if roll < self.base_win_probability:
            amount = bet * self.payout_ratio
            return GamblingOutcome(
                success=True,
                monetary_change=amount,
                was_near_miss=False,
                psychological_impact=0.2
            )
        elif roll < self.base_win_probability + self.near_miss_probability:
            return GamblingOutcome(
                success=False,
                monetary_change=0.0,
                was_near_miss=True,
                psychological_impact=0.1
            )
        else:
            return GamblingOutcome(
                success=False,
                monetary_change=-bet,
                was_near_miss=False,
                psychological_impact=-0.1
            )


class Casino(Building):
    """Casino building containing multiple gambling games."""
    def __init__(
        self,
        building_id,
        plot,
        games: List[GamblingGame],
        house_edge: float = 0.05
    ):
        super().__init__(building_id, plot)
        self.games = games
        self.house_edge = house_edge
        self.cue_base_intensity = 0.5
        self.cue_influence_radius = 2.0

    def get_available_games(self) -> List[GamblingGame]:
        """Return list of available games."""
        return self.games

    def generate_cues(self, agent_location: PlotID) -> List[GamblingCue]:
        """Generate gambling cues based on presence of casino."""
        # This method is now mainly for backward compatibility
        # The main cue generation is handled by CueGenerator
        return [GamblingCue(intensity=self.cue_base_intensity, source=self.plot.id)]

    def can_interact(self, agent) -> bool:
        """Agents can interact if they can afford minimum bet."""
        if not self.games:
            return False
        # Check if agent has enough money for smallest bet
        min_bet = min(game.min_bet for game in self.games)
        return agent.internal_state.wealth >= min_bet

    def __repr__(self) -> str:
        return (
            f"Casino(id={self.id}, games={len(self.games)}, house_edge={self.house_edge})"
        ) 
