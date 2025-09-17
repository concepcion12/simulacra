"""
Metrics system for tracking agent-level and population-level statistics.
Implements Phase 7.1 of the roadmap.
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime

from simulacra.utils.types import (
    AgentID, ActionType, BehaviorType, SubstanceType
)
from simulacra.agents.agent import Agent


@dataclass
class AgentMetrics:
    """Comprehensive metrics for an individual agent."""
    # Identity
    agent_id: AgentID
    timestamp: datetime

    # Financial metrics
    wealth: float
    income_last_month: float = 0.0
    expenses_last_month: float = 0.0
    wealth_change: float = 0.0
    poverty_line_ratio: float = 0.0  # wealth / poverty_line

    # Employment metrics
    employed: bool = False
    employment_duration: int = 0  # months
    job_changes: int = 0
    work_performance: float = 0.0

    # Housing metrics
    housed: bool = False
    housing_duration: int = 0  # months
    housing_quality: float = 0.0
    eviction_count: int = 0

    # Mental health metrics
    stress_level: float = 0.0
    mood_level: float = 0.0
    self_control: float = 0.0

    # Addiction metrics
    alcohol_addiction_level: float = 0.0
    alcohol_consumption_frequency: float = 0.0
    alcohol_tolerance: float = 0.0
    alcohol_withdrawal_severity: float = 0.0

    # Behavioral metrics
    gambling_frequency: float = 0.0
    gambling_habit_strength: float = 0.0
    gambling_wins: int = 0
    gambling_losses: int = 0
    gambling_net_outcome: float = 0.0

    # Action patterns
    action_diversity: float = 0.0  # Shannon entropy of action distribution
    most_frequent_action: Optional[ActionType] = None
    action_success_rate: float = 0.0

    # Social metrics
    isolation_score: float = 0.0  # 0 = well connected, 1 = isolated

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for export."""
        return asdict(self)


@dataclass
class PopulationMetrics:
    """Aggregate metrics for the entire population."""
    timestamp: datetime
    total_agents: int

    # Economic metrics
    mean_wealth: float
    median_wealth: float
    wealth_std: float
    wealth_gini_coefficient: float
    poverty_rate: float  # % below poverty line

    # Employment
    employment_rate: float
    unemployment_duration_mean: float
    job_turnover_rate: float

    # Housing
    homelessness_rate: float
    housing_instability_rate: float  # % at risk of eviction

    # Health metrics
    mean_stress: float
    mean_mood: float
    high_stress_rate: float  # % with stress > 0.7

    # Addiction prevalence
    addiction_rate: float  # % with addiction level > 0.5
    heavy_drinking_rate: float
    problem_gambling_rate: float

    # Behavioral patterns
    action_distribution: Dict[ActionType, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for export."""
        return asdict(self)


@dataclass
class BehavioralPattern:
    """Identified behavioral pattern in agent population."""
    pattern_id: str
    pattern_type: str  # 'addiction_spiral', 'recovery', 'stable_employment', etc.
    agent_count: int
    avg_duration: float  # months
    characteristics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for export."""
        return asdict(self)


@dataclass
class EconomicIndicators:
    """City-wide economic indicators."""
    timestamp: datetime

    # Market indicators
    unemployment_rate: float
    inflation_rate: float
    housing_vacancy_rate: float
    average_rent: float
    average_wage: float

    # Distribution metrics
    income_inequality: float  # Gini coefficient
    wealth_mobility: float  # % changing wealth quintile

    # Sector-specific
    liquor_store_revenue: float
    casino_revenue: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert indicators to dictionary for export."""
        return asdict(self)


class MetricsCollector:
    """
    Central metrics collection system.
    Collects, aggregates, and analyzes simulation data.
    """

    def __init__(self, poverty_line: float = 800.0):
        """
        Initialize metrics collector.

        Args:
            poverty_line: Monthly income threshold for poverty
        """
        self.poverty_line = poverty_line

        # Storage for current metrics
        self.agent_metrics: Dict[AgentID, AgentMetrics] = {}
        self.population_metrics_history: List[PopulationMetrics] = []
        self.round_metrics_history: List[PopulationMetrics] = []
        self.economic_indicators_history: List[EconomicIndicators] = []
        self.behavioral_patterns: List[BehavioralPattern] = []

        # Tracking for metrics calculation
        self.agent_action_counts: Dict[AgentID, Counter] = defaultdict(Counter)
        self.agent_action_successes: Dict[AgentID, int] = defaultdict(int)
        self.agent_total_actions: Dict[AgentID, int] = defaultdict(int)

        # Employment/unemployment tracking
        self.unemployment_durations: Dict[AgentID, int] = defaultdict(int)
        self.previous_employment: Dict[AgentID, Optional[Tuple[Any, Any]]] = {}
        self.agent_job_changes: Dict[AgentID, int] = defaultdict(int)

        # Pattern membership tracking
        self.pattern_members: Dict[str, Dict[AgentID, int]] = defaultdict(dict)
        self.monthly_job_changes = 0

    def _update_employment_tracking(self, agent: Agent) -> bool:
        """Update unemployment duration and detect job changes."""
        current = (
            agent.employment.employer_id if agent.employment else None,
            agent.employment.job_id if agent.employment else None,
        )

        prev = self.previous_employment.get(agent.id)

        # Update unemployment duration
        if agent.employment is None:
            self.unemployment_durations[agent.id] += 1
        else:
            self.unemployment_durations[agent.id] = 0

        changed = False
        if prev is not None and prev != current:
            self.agent_job_changes[agent.id] += 1
            self.monthly_job_changes += 1
            changed = True

        self.previous_employment[agent.id] = current
        return changed

    def collect_agent_metrics(self, agent: Agent, timestamp: datetime) -> AgentMetrics:
        """
        Collect comprehensive metrics for a single agent.

        Args:
            agent: Agent to collect metrics from
            timestamp: Current timestamp

        Returns:
            Collected agent metrics
        """
        # Update employment/unemployment tracking
        self._update_employment_tracking(agent)

        # Calculate action metrics from history
        action_diversity = self._calculate_action_diversity(agent.id)
        most_frequent = self._get_most_frequent_action(agent.id)
        success_rate = self._calculate_action_success_rate(agent.id)

        # Calculate behavioral frequencies from recent history
        alcohol_frequency = self._calculate_behavior_frequency(
            agent, ActionType.DRINK, lookback=10
        )
        gambling_frequency = self._calculate_behavior_frequency(
            agent, ActionType.GAMBLE, lookback=10
        )

        # Get addiction state
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]

        # Calculate financial metrics
        wealth_change = 0.0  # Would need previous wealth to calculate
        if agent.id in self.agent_metrics:
            wealth_change = agent.internal_state.wealth - self.agent_metrics[agent.id].wealth

        # Calculate employment metrics
        employment_duration = 0
        work_performance = 0.0
        if agent.employment:
            employment_duration = agent.employment.performance_history.months_employed
            work_performance = agent.employment.performance_history.average_performance

        metrics = AgentMetrics(
            agent_id=agent.id,
            timestamp=timestamp,

            # Financial
            wealth=agent.internal_state.wealth,
            wealth_change=wealth_change,
            poverty_line_ratio=agent.internal_state.wealth / self.poverty_line,

            # Employment
            employed=agent.employment is not None,
            employment_duration=employment_duration,
            job_changes=self.agent_job_changes.get(agent.id, 0),
            work_performance=work_performance,

            # Housing
            housed=agent.home is not None,
            housing_quality=agent.home.quality if agent.home else 0.0,

            # Mental health
            stress_level=agent.internal_state.stress,
            mood_level=agent.internal_state.mood,
            self_control=agent.internal_state.self_control_resource,

            # Addiction
            alcohol_addiction_level=alcohol_state.stock,
            alcohol_consumption_frequency=alcohol_frequency,
            alcohol_tolerance=alcohol_state.tolerance_level,
            alcohol_withdrawal_severity=alcohol_state.withdrawal_severity,

            # Gambling
            gambling_frequency=gambling_frequency,
            gambling_habit_strength=agent.habit_stocks[BehaviorType.GAMBLING],
            gambling_net_outcome=agent.gambling_context.total_wins,

            # Action patterns
            action_diversity=action_diversity,
            most_frequent_action=most_frequent,
            action_success_rate=success_rate,

            # Social (simplified for now)
            isolation_score=1.0 if not agent.home and not agent.employment else 0.0
        )

        self.agent_metrics[agent.id] = metrics
        return metrics

    def collect_population_metrics(
        self,
        agents: List[Agent],
        timestamp: datetime,
        store_history: bool = True
    ) -> PopulationMetrics:
        """
        Collect aggregate metrics for entire population.

        Args:
            agents: List of all agents
            timestamp: Current timestamp

        Returns:
            Population-level metrics
        """
        if not agents:
            return PopulationMetrics(
                timestamp=timestamp,
                total_agents=0,
                mean_wealth=0,
                median_wealth=0,
                wealth_std=0,
                wealth_gini_coefficient=0,
                poverty_rate=0,
                employment_rate=0,
                unemployment_duration_mean=0,
                job_turnover_rate=0,
                homelessness_rate=0,
                housing_instability_rate=0,
                mean_stress=0,
                mean_mood=0,
                high_stress_rate=0,
                addiction_rate=0,
                heavy_drinking_rate=0,
                problem_gambling_rate=0
            )

        # Collect individual metrics first and track job changes
        self.monthly_job_changes = 0
        for agent in agents:
            self.collect_agent_metrics(agent, timestamp)

        # Financial metrics
        wealths = [agent.internal_state.wealth for agent in agents]
        mean_wealth = np.mean(wealths)
        median_wealth = np.median(wealths)
        wealth_std = np.std(wealths)
        wealth_gini = self._calculate_gini_coefficient(wealths)
        poverty_rate = sum(1 for w in wealths if w < self.poverty_line) / len(agents)

        # Employment metrics
        employed_count = sum(1 for agent in agents if agent.employment is not None)
        employment_rate = employed_count / len(agents)

        # Housing metrics
        homeless_count = sum(1 for agent in agents if agent.home is None)
        homelessness_rate = homeless_count / len(agents)

        # Calculate housing instability (low wealth + high rent)
        at_risk_count = sum(
            1 for agent in agents
            if agent.home and agent.internal_state.wealth < agent.home.monthly_rent * 2
        )
        housing_instability_rate = at_risk_count / len(agents)

        # Health metrics
        stress_levels = [agent.internal_state.stress for agent in agents]
        mean_stress = np.mean(stress_levels)
        high_stress_rate = sum(1 for s in stress_levels if s > 0.7) / len(agents)

        mood_levels = [agent.internal_state.mood for agent in agents]
        mean_mood = np.mean(mood_levels)

        # Addiction metrics
        addiction_count = sum(
            1 for agent in agents
            if agent.addiction_states[SubstanceType.ALCOHOL].stock > 0.5
        )
        addiction_rate = addiction_count / len(agents)

        heavy_drinking_count = sum(
            1 for agent in agents
            if self._calculate_behavior_frequency(agent, ActionType.DRINK, 10) > 0.3
        )
        heavy_drinking_rate = heavy_drinking_count / len(agents)

        problem_gambling_count = sum(
            1 for agent in agents
            if agent.habit_stocks[BehaviorType.GAMBLING] > 0.5
        )
        problem_gambling_rate = problem_gambling_count / len(agents)

        # Unemployment metrics
        unemployed_durations = [
            self.unemployment_durations[agent.id]
            for agent in agents
            if agent.employment is None
        ]
        unemployment_duration_mean = (
            float(np.mean(unemployed_durations)) if unemployed_durations else 0.0
        )

        # Job turnover metrics
        job_turnover_rate = self.monthly_job_changes / len(agents)
        self.monthly_job_changes = 0

        # Action distribution
        action_distribution = self._calculate_population_action_distribution(agents)

        metrics = PopulationMetrics(
            timestamp=timestamp,
            total_agents=len(agents),
            mean_wealth=mean_wealth,
            median_wealth=median_wealth,
            wealth_std=wealth_std,
            wealth_gini_coefficient=wealth_gini,
            poverty_rate=poverty_rate,
            employment_rate=employment_rate,
            unemployment_duration_mean=unemployment_duration_mean,
            job_turnover_rate=job_turnover_rate,
            homelessness_rate=homelessness_rate,
            housing_instability_rate=housing_instability_rate,
            mean_stress=mean_stress,
            mean_mood=mean_mood,
            high_stress_rate=high_stress_rate,
            addiction_rate=addiction_rate,
            heavy_drinking_rate=heavy_drinking_rate,
            problem_gambling_rate=problem_gambling_rate,
            action_distribution=action_distribution
        )

        if store_history:
            self.population_metrics_history.append(metrics)
        return metrics

    def collect_round_metrics(
        self,
        agents: List[Agent],
        timestamp: datetime
    ) -> PopulationMetrics:
        """Collect and store metrics for an individual action round."""
        metrics = self.collect_population_metrics(
            agents,
            timestamp,
            store_history=False
        )
        self.round_metrics_history.append(metrics)
        return metrics

    def identify_behavioral_patterns(self, agents: List[Agent]) -> List[BehavioralPattern]:
        """
        Identify common behavioral patterns in the population.

        Args:
            agents: List of agents to analyze

        Returns:
            List of identified patterns
        """
        patterns = []

        # Addiction spiral pattern
        addiction_spiral_agents = [
            agent for agent in agents
            if (
                agent.addiction_states[SubstanceType.ALCOHOL].stock > 0.7
                and agent.internal_state.wealth < self.poverty_line
                and agent.internal_state.stress > 0.7
            )
        ]

        if addiction_spiral_agents:
            pattern_id = "addiction_spiral"
            current_members = {}
            durations = []
            for agent in addiction_spiral_agents:
                prev = self.pattern_members[pattern_id].get(agent.id, 0)
                duration = prev + 1
                current_members[agent.id] = duration
                durations.append(duration)
            self.pattern_members[pattern_id] = current_members

            patterns.append(
                BehavioralPattern(
                    pattern_id=pattern_id,
                    pattern_type="addiction_spiral",
                    agent_count=len(addiction_spiral_agents),
                    avg_duration=float(np.mean(durations)) if durations else 0.0,
                    characteristics={
                        "avg_addiction_level": np.mean([
                            agent.addiction_states[SubstanceType.ALCOHOL].stock
                            for agent in addiction_spiral_agents
                        ]),
                        "avg_wealth": np.mean([
                            agent.internal_state.wealth
                            for agent in addiction_spiral_agents
                        ]),
                        "employment_rate": sum(
                            1 for agent in addiction_spiral_agents
                            if agent.employment is not None
                        ) / len(addiction_spiral_agents)
                    },
                )
            )

        # Stable employment pattern
        stable_employment_agents = [
            agent for agent in agents
            if (agent.employment is not None and
                agent.employment.performance_history.months_employed > 6 and
                agent.employment.performance_history.average_performance > 0.7)
        ]

        if stable_employment_agents:
            patterns.append(BehavioralPattern(
                pattern_id="stable_employment",
                pattern_type="stable_employment",
                agent_count=len(stable_employment_agents),
                avg_duration=np.mean([
                    agent.employment.performance_history.months_employed
                    for agent in stable_employment_agents
                ]),
                characteristics={
                    "avg_wealth": np.mean([
                        agent.internal_state.wealth
                        for agent in stable_employment_agents
                    ]),
                    "avg_stress": np.mean([
                        agent.internal_state.stress
                        for agent in stable_employment_agents
                    ]),
                    "addiction_rate": sum(
                        1 for agent in stable_employment_agents
                        if agent.addiction_states[SubstanceType.ALCOHOL].stock > 0.5
                    ) / len(stable_employment_agents)
                }
            ))

        self.behavioral_patterns.extend(patterns)
        return patterns

    def record_action(self, agent_id: AgentID, action_type: ActionType, success: bool) -> None:
        """
        Record an agent action for metrics calculation.

        Args:
            agent_id: ID of agent taking action
            action_type: Type of action taken
            success: Whether action was successful
        """
        self.agent_action_counts[agent_id][action_type] += 1
        self.agent_total_actions[agent_id] += 1
        if success:
            self.agent_action_successes[agent_id] += 1

    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement."""
        if not values or len(values) < 2:
            return 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)

        # Calculate Gini using the formula
        cumsum = 0
        for i, value in enumerate(sorted_values):
            cumsum += (2 * (i + 1) - n - 1) * value

        return cumsum / (n * sum(sorted_values))

    def _calculate_action_diversity(self, agent_id: AgentID) -> float:
        """Calculate Shannon entropy of agent's action distribution."""
        counts = self.agent_action_counts.get(agent_id)
        if not counts:
            return 0.0

        total = sum(counts.values())
        if total == 0:
            return 0.0

        # Calculate Shannon entropy
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(ActionType))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _get_most_frequent_action(self, agent_id: AgentID) -> Optional[ActionType]:
        """Get agent's most frequently taken action."""
        counts = self.agent_action_counts.get(agent_id)
        if not counts:
            return None

        return max(counts.items(), key=lambda x: x[1])[0]

    def _calculate_action_success_rate(self, agent_id: AgentID) -> float:
        """Calculate agent's overall action success rate."""
        total = self.agent_total_actions.get(agent_id, 0)
        if total == 0:
            return 0.0

        successes = self.agent_action_successes.get(agent_id, 0)
        return successes / total

    def _calculate_behavior_frequency(
        self,
        agent: Agent,
        action_type: ActionType,
        lookback: int = 10
    ) -> float:
        """Calculate frequency of a behavior in recent history."""
        if not agent.action_history:
            return 0.0

        recent_actions = list(agent.action_history)[-lookback:]
        behavior_count = sum(
            1 for action, _ in recent_actions
            if action.action_type == action_type
        )

        return behavior_count / len(recent_actions)

    def _calculate_population_action_distribution(
        self,
        agents: List[Agent]
    ) -> Dict[ActionType, float]:
        """Calculate distribution of actions across population."""
        total_counts = Counter()

        for agent_id, counts in self.agent_action_counts.items():
            total_counts.update(counts)

        total_actions = sum(total_counts.values())
        if total_actions == 0:
            return {}

        return {
            action_type: count / total_actions
            for action_type, count in total_counts.items()
        }

    def get_agent_metrics(self, agent_id: AgentID) -> Optional[AgentMetrics]:
        """Get current metrics for specific agent."""
        return self.agent_metrics.get(agent_id)

    def get_latest_population_metrics(self) -> Optional[PopulationMetrics]:
        """Get most recent population metrics."""
        return self.population_metrics_history[-1] if self.population_metrics_history else None

    def clear_action_tracking(self) -> None:
        """Clear action tracking data (e.g., at month boundaries)."""
        self.agent_action_counts.clear()
        self.agent_action_successes.clear()
        self.agent_total_actions.clear()
