"""
Environmental Cue System for Simulacra simulation.

This module handles the generation and processing of environmental cues that influence
agent behavior based on spatial proximity, temporal factors, and agent internal state.
"""
import math
from typing import List, Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass

from simulacra.utils.types import (
    EnvironmentalCue, AlcoholCue, GamblingCue, FinancialStressCue,
    CueType, PlotID, Coordinate, SimulationTime, PlotType
)
from simulacra.environment.spatial import euclidean_distance

if TYPE_CHECKING:
    from simulacra.agents.agent import Agent
    from simulacra.environment.city import City
    from simulacra.environment.buildings.base import Building


@dataclass
class CueSource:
    """Represents a source of environmental cues."""
    plot_id: PlotID
    location: Coordinate
    cue_type: CueType
    base_intensity: float
    influence_radius: float
    building_type: Optional[PlotType] = None


class CueGenerator:
    """
    Generates environmental cues based on spatial proximity, temporal factors,
    and agent state.
    """

    # Base parameters for cue generation
    DEFAULT_INFLUENCE_RADIUS = 3.0  # Maximum distance for cue effects
    INTENSITY_DECAY_RATE = 2.0  # Exponential decay rate with distance

    # Cue type specific parameters
    CUE_PARAMETERS = {
        CueType.ALCOHOL_CUE: {
            'base_intensity': 0.6,
            'influence_radius': 2.5,
            'agent_state_amplifier': 1.5  # How much agent addiction state amplifies
        },
        CueType.GAMBLING_CUE: {
            'base_intensity': 0.5,
            'influence_radius': 2.0,
            'agent_state_amplifier': 1.3
        },
        CueType.FINANCIAL_STRESS_CUE: {
            'base_intensity': 0.4,
            'influence_radius': 1.5,
            'agent_state_amplifier': 1.2
        }
    }

    def __init__(self):
        """Initialize the cue generator."""
        self._cue_sources_cache: Dict[PlotID, List[CueSource]] = {}
        self._last_cache_update = 0
        self._precomputed = False

    def precompute_city_cue_sources(self, city: 'City') -> None:
        """Precompute cue sources for all buildings in the city."""
        self._cue_sources_cache = {}
        for district in city.districts:
            for plot in district.plots:
                if plot.building is not None:
                    sources = self._get_building_cue_sources(plot.building)
                    if sources:
                        self._cue_sources_cache[plot.id] = sources
        self._precomputed = True

    def generate_spatial_cues(
        self,
        agent: 'Agent',
        city: 'City'
    ) -> List[EnvironmentalCue]:
        """
        Generate environmental cues based on agent's spatial location.

        Args:
            agent: The agent experiencing cues
            city: The city environment

        Returns:
            List of environmental cues affecting the agent
        """
        if agent.current_location is None:
            return []

        # Get agent's current plot and location
        agent_plot = city.get_plot(agent.current_location)
        if agent_plot is None:
            return []

        agent_location = agent_plot.location
        cues = []

        # Find all potential cue sources within influence range
        cue_sources = self._get_nearby_cue_sources(agent_location, city)

        for source in cue_sources:
            # Calculate distance-based intensity
            distance = euclidean_distance(agent_location, source.location)

            if distance <= source.influence_radius:
                # Generate cue with distance-modulated intensity
                intensity = self.calculate_cue_intensity(
                    distance,
                    source.base_intensity,
                    source.influence_radius
                )

                # Apply agent state modulation
                modulated_intensity = self._apply_agent_state_modulation(
                    intensity, source.cue_type, agent
                )

                if modulated_intensity > 0.01:  # Only include meaningful cues
                    cue = self._create_cue(source.cue_type, modulated_intensity, source.plot_id)
                    if cue:
                        cues.append(cue)

        return cues

    def generate_temporal_cues(
        self,
        agent: 'Agent',
        time: SimulationTime
    ) -> List[EnvironmentalCue]:
        """
        Generate temporal cues based on time of day/month and agent history.

        Args:
            agent: The agent experiencing cues
            time: Current simulation time

        Returns:
            List of temporal environmental cues
        """
        cues = []

        # Financial stress cues based on monthly cycle
        if self._is_rent_due_soon(time):
            # Increase financial stress near end of month
            stress_intensity = self._calculate_financial_stress_intensity(agent, time)
            if stress_intensity > 0:
                cue = FinancialStressCue(
                    intensity=stress_intensity,
                    source=None  # Temporal cue has no spatial source
                )
                cues.append(cue)

        # Addiction withdrawal cues
        withdrawal_cues = self._generate_withdrawal_cues(agent)
        cues.extend(withdrawal_cues)

        # Habitual timing cues (e.g., usual drinking times)
        habit_cues = self._generate_habit_timing_cues(agent, time)
        cues.extend(habit_cues)

        return cues

    def generate_social_cues(
        self,
        agent: 'Agent',
        nearby_agents: List['Agent']
    ) -> List[EnvironmentalCue]:
        """
        Generate social cues from observing other agents' behaviors.

        Args:
            agent: The agent experiencing cues
            nearby_agents: Other agents in the vicinity

        Returns:
            List of social environmental cues
        """
        cues = []
        from simulacra.utils.types import BehaviorType

        for other in nearby_agents:
            # Drinking modeling
            drink_habit = getattr(other, 'habit_stocks', {}).get(BehaviorType.DRINKING, 0.0)
            if drink_habit > 0.5:
                intensity = drink_habit * 0.5
                cues.append(AlcoholCue(intensity=intensity, source=other.id))

            # Gambling modeling
            gamble_habit = getattr(other, 'habit_stocks', {}).get(BehaviorType.GAMBLING, 0.0)
            if gamble_habit > 0.5:
                intensity = gamble_habit * 0.4
                cues.append(GamblingCue(intensity=intensity, source=other.id))

        return cues

    def generate_cues_for_agent(
        self,
        agent: 'Agent',
        city: 'City',
        time: Optional[SimulationTime] = None,
        nearby_agents: Optional[List['Agent']] = None
    ) -> List[EnvironmentalCue]:
        """
        Generate all environmental cues for an agent.

        This unified method combines spatial, temporal, and social cues into one call.

        Args:
            agent: The agent experiencing cues
            city: The city environment
            time: Current simulation time (optional, will use agent's current time if available)
            nearby_agents: Other agents in vicinity (optional, will be found automatically)

        Returns:
            Combined list of all environmental cues affecting the agent
        """
        all_cues = []

        # Generate spatial cues
        spatial_cues = self.generate_spatial_cues(agent, city)
        all_cues.extend(spatial_cues)

        # Generate temporal cues
        if time is None:
            # Try to get time from agent's current context or use a default
            # For now, we'll create a basic time if none provided
            from simulacra.utils.types import SimulationTime
            time = SimulationTime(month=1, year=1)

        temporal_cues = self.generate_temporal_cues(agent, time)
        all_cues.extend(temporal_cues)

        # Generate social cues
        if nearby_agents is None:
            # Find nearby agents automatically
            nearby_agents = self._find_nearby_agents(agent, city)

        social_cues = self.generate_social_cues(agent, nearby_agents)
        all_cues.extend(social_cues)

        return all_cues

    def _find_nearby_agents(self, agent: 'Agent', city: 'City') -> List['Agent']:
        """
        Find agents near the given agent.

        Args:
            agent: The reference agent
            city: The city environment

        Returns:
            List of nearby agents
        """
        nearby_agents = []

        if agent.current_location is None:
            return nearby_agents

        # Get agent's current plot
        agent_plot = city.get_plot(agent.current_location)
        if agent_plot is None:
            return nearby_agents

        agent_location = agent_plot.location
        search_radius = 2.0  # Search within 2 units

        # Search through all districts and plots to find other agents
        for district in city.districts:
            for plot in district.plots:
                if plot.building is None:
                    continue

                # Check if there are agents at this plot
                distance = euclidean_distance(agent_location, plot.location)
                if distance <= search_radius:
                    # This is a simplified approach - in a full implementation,
                    # we'd need access to all agents' locations from the simulation
                    # For now, return empty list as social cues are minimal anyway
                    pass

        return nearby_agents

    def calculate_cue_intensity(
        self,
        distance: float,
        base_intensity: float,
        max_radius: float = None
    ) -> float:
        """
        Calculate cue intensity based on distance from source.

        Uses inverse square law with exponential decay for realistic falloff.

        Args:
            distance: Distance from cue source
            base_intensity: Base intensity at source
            max_radius: Maximum influence radius

        Returns:
            Distance-modulated intensity [0,1]
        """
        if distance <= 0:
            return base_intensity

        max_radius = max_radius or self.DEFAULT_INFLUENCE_RADIUS

        if distance > max_radius:
            return 0.0

        # Inverse square law with exponential decay
        # I(d) = I₀ * exp(-λd) / (1 + d²)
        exponential_decay = math.exp(-self.INTENSITY_DECAY_RATE * distance / max_radius)
        inverse_square = 1.0 / (1.0 + distance ** 2)

        intensity = base_intensity * exponential_decay * inverse_square

        return max(0.0, min(1.0, intensity))

    def _get_nearby_cue_sources(
        self,
        agent_location: Coordinate,
        city: 'City'
    ) -> List[CueSource]:
        """Get all cue sources within potential influence range."""
        if not self._precomputed:
            self.precompute_city_cue_sources(city)

        sources = []
        max_search_radius = self.DEFAULT_INFLUENCE_RADIUS * 1.5

        for plot_id, cue_sources in self._cue_sources_cache.items():
            plot = city.get_plot(plot_id)
            if plot is None:
                continue
            distance = euclidean_distance(agent_location, plot.location)
            if distance <= max_search_radius:
                sources.extend(cue_sources)

        return sources

    def _get_building_cue_sources(self, building: 'Building') -> List[CueSource]:
        """Extract cue sources from a building."""
        if building.plot.id in self._cue_sources_cache:
            return self._cue_sources_cache[building.plot.id]

        sources = []

        # Map building types to cue types
        building_cue_mapping = {
            'LiquorStore': CueType.ALCOHOL_CUE,
            'Casino': CueType.GAMBLING_CUE,
        }

        building_type_name = type(building).__name__
        cue_type = building_cue_mapping.get(building_type_name)

        if cue_type and cue_type in self.CUE_PARAMETERS:
            params = self.CUE_PARAMETERS[cue_type]
            source = CueSource(
                plot_id=building.plot.id,
                location=building.plot.location,
                cue_type=cue_type,
                base_intensity=params['base_intensity'],
                influence_radius=params['influence_radius']
            )
            sources.append(source)

        self._cue_sources_cache[building.plot.id] = sources
        return sources

    def _apply_agent_state_modulation(
        self,
        base_intensity: float,
        cue_type: CueType,
        agent: 'Agent'
    ) -> float:
        """
        Modulate cue intensity based on agent's internal state.

        Args:
            base_intensity: Base intensity from spatial calculation
            cue_type: Type of cue
            agent: Agent experiencing the cue

        Returns:
            State-modulated intensity
        """
        intensity = base_intensity
        params = self.CUE_PARAMETERS.get(cue_type, {})
        amplifier = params.get('agent_state_amplifier', 1.0)

        if cue_type == CueType.ALCOHOL_CUE:
            # Alcohol cues amplified by addiction state and stress
            from simulacra.utils.types import SubstanceType
            addiction_state = agent.addiction_states.get(SubstanceType.ALCOHOL)
            if addiction_state:
                # Higher addiction stock increases sensitivity
                addiction_amp = 1.0 + addiction_state.stock * (amplifier - 1.0)
                intensity *= addiction_amp

                # Withdrawal amplifies cue reception
                if addiction_state.withdrawal_severity > 0:
                    withdrawal_amp = 1.0 + addiction_state.withdrawal_severity * 0.5
                    intensity *= withdrawal_amp

            # High stress makes alcohol cues more salient
            if agent.internal_state.stress > 0.6:
                stress_amp = 1.0 + (agent.internal_state.stress - 0.6) * 0.3
                intensity *= stress_amp

        elif cue_type == CueType.GAMBLING_CUE:
            # Gambling cues amplified by habit and financial pressure
            from simulacra.utils.types import BehaviorType
            gambling_habit = agent.habit_stocks.get(BehaviorType.GAMBLING, 0.0)
            if gambling_habit > 0:
                habit_amp = 1.0 + gambling_habit * (amplifier - 1.0)
                intensity *= habit_amp

            # Financial pressure amplifies gambling cues
            expense_ratio = agent.internal_state.monthly_expenses / max(agent.internal_state.wealth, 1)
            if expense_ratio > 1.0:  # Can't afford expenses
                financial_pressure_amp = 1.0 + min(expense_ratio - 1.0, 1.0) * 0.4
                intensity *= financial_pressure_amp

        elif cue_type == CueType.FINANCIAL_STRESS_CUE:
            # Financial stress cues amplified by actual financial situation
            expense_ratio = agent.internal_state.monthly_expenses / max(agent.internal_state.wealth, 1)
            if expense_ratio > 0.8:
                financial_amp = 1.0 + (expense_ratio - 0.8) * (amplifier - 1.0)
                intensity *= financial_amp

        return min(1.0, intensity)

    def _create_cue(
        self,
        cue_type: CueType,
        intensity: float,
        source: PlotID
    ) -> Optional[EnvironmentalCue]:
        """Create appropriate cue object based on type."""
        if cue_type == CueType.ALCOHOL_CUE:
            return AlcoholCue(intensity=intensity, source=source)
        elif cue_type == CueType.GAMBLING_CUE:
            return GamblingCue(intensity=intensity, source=source)
        elif cue_type == CueType.FINANCIAL_STRESS_CUE:
            return FinancialStressCue(intensity=intensity, source=source)
        else:
            return None

    def _is_rent_due_soon(self, time: SimulationTime) -> bool:
        """Check if rent is due soon (last week of month)."""
        return time.month_progress > 0.75

    def _calculate_financial_stress_intensity(
        self,
        agent: 'Agent',
        time: SimulationTime
    ) -> float:
        """Calculate intensity of financial stress cues."""
        # Base stress from inability to pay expenses
        expense_ratio = agent.internal_state.monthly_expenses / max(agent.internal_state.wealth, 1)

        if expense_ratio <= 0.8:
            return 0.0  # No financial stress

        base_intensity = min(1.0, (expense_ratio - 0.8) / 0.4)  # Scale 0.8-1.2 to 0-1

        # Amplify near end of month
        time_amplifier = 1.0 + time.month_progress * 0.5

        return min(1.0, base_intensity * time_amplifier)

    def _generate_withdrawal_cues(self, agent: 'Agent') -> List[EnvironmentalCue]:
        """Generate cues from addiction withdrawal."""
        cues = []

        # Alcohol withdrawal
        from simulacra.utils.types import SubstanceType
        addiction_states = getattr(agent, "addiction_states", {})
        if not isinstance(addiction_states, dict):
            addiction_states = {}
        alcohol_state = addiction_states.get(SubstanceType.ALCOHOL)
        if alcohol_state and alcohol_state.withdrawal_severity > 0.3:
            # Internal withdrawal creates craving cues
            intensity = min(1.0, alcohol_state.withdrawal_severity * 1.2)
            cue = AlcoholCue(intensity=intensity, source=None)
            cues.append(cue)

        return cues

    def _generate_habit_timing_cues(
        self,
        agent: 'Agent',
        time: SimulationTime
    ) -> List[EnvironmentalCue]:
        """Generate cues based on habitual timing patterns."""
        cues = []

        # Simple implementation: habits create mild background cues
        from simulacra.utils.types import BehaviorType
        habit_stocks = getattr(agent, "habit_stocks", {})
        if not isinstance(habit_stocks, dict):
            habit_stocks = {}
        drinking_habit = habit_stocks.get(BehaviorType.DRINKING, 0.0)
        if drinking_habit > 0.3:
            # Habitual drinking creates mild cues at habitual times
            intensity = drinking_habit * 0.3
            cue = AlcoholCue(intensity=intensity, source=None)
            cues.append(cue)

        gambling_habit = habit_stocks.get(BehaviorType.GAMBLING, 0.0)
        if gambling_habit > 0.3:
            intensity = gambling_habit * 0.25
            cue = GamblingCue(intensity=intensity, source=None)
            cues.append(cue)

        return cues
