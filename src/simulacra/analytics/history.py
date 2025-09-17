"""
History tracking system for detailed agent data collection.
Implements Phase 7.2 of the roadmap.
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from simulacra.utils.types import (
    AgentID, ActionType, PlotID, BuildingID,
    InternalState, PersonalityTraits,
    BehaviorType, SubstanceType
)
from simulacra.agents.agent import Agent
from simulacra.agents.decision_making import Action
from simulacra.agents.action_outcomes import ActionOutcome


class EventType(Enum):
    """Types of life events that can occur."""
    # Employment events
    JOB_GAINED = "job_gained"
    JOB_LOST = "job_lost"
    JOB_CHANGED = "job_changed"
    PROMOTION = "promotion"
    DEMOTION = "demotion"

    # Housing events
    HOUSING_GAINED = "housing_gained"
    HOUSING_LOST = "housing_lost"
    HOUSING_CHANGED = "housing_changed"
    EVICTED = "evicted"

    # Financial events
    BANKRUPT = "bankrupt"
    WINDFALL = "windfall"
    SALARY_RECEIVED = "salary_received"
    RENT_PAID = "rent_paid"

    # Health/addiction events
    ADDICTION_ONSET = "addiction_onset"
    ADDICTION_RECOVERY = "addiction_recovery"
    OVERDOSE = "overdose"
    HOSPITALIZATION = "hospitalization"

    # Social events
    RELATIONSHIP_FORMED = "relationship_formed"
    RELATIONSHIP_ENDED = "relationship_ended"

    # Gambling events
    BIG_WIN = "big_win"
    BIG_LOSS = "big_loss"
    GAMBLING_ADDICTION_ONSET = "gambling_addiction_onset"


@dataclass
class StateSnapshot:
    """Complete snapshot of agent state at a point in time."""
    timestamp: datetime

    # Location
    current_location: Optional[PlotID]

    # Financial state
    wealth: float
    monthly_income: float
    monthly_expenses: float

    # Employment
    employed: bool

    # Housing
    housed: bool

    # Mental state
    mood: float
    stress: float
    self_control: float

    # Addiction state
    alcohol_addiction_level: float
    alcohol_tolerance: float
    alcohol_withdrawal: float
    time_since_last_drink: int

    # Gambling state
    gambling_habit_strength: float
    gambling_total_winnings: float
    actions_taken_this_month: int
    time_budget_remaining: float

    # Optional fields with defaults (must come after non-default fields)
    employment_info: Optional[Dict[str, Any]] = None
    housing_info: Optional[Dict[str, Any]] = None
    recent_gambling_outcomes: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_agent(cls, agent: Agent, timestamp: datetime) -> 'StateSnapshot':
        """Create snapshot from current agent state."""
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]

        monthly_income = 0.0
        employment_info: Optional[Dict[str, Any]] = None
        if agent.employment is not None:
            base_salary = getattr(agent.employment, 'base_salary', 0.0)
            performance = getattr(
                agent.employment.performance_history,
                'average_performance',
                1.0
            )
            monthly_income = base_salary * performance
            employment_info = asdict(agent.employment)

        housing_info = asdict(agent.home) if agent.home else None

        snapshot = cls(
            timestamp=timestamp,
            current_location=agent.current_location,
            wealth=agent.internal_state.wealth,
            monthly_income=monthly_income,
            monthly_expenses=agent.internal_state.monthly_expenses,
            employed=agent.employment is not None,
            housed=agent.home is not None,
            mood=agent.internal_state.mood,
            stress=agent.internal_state.stress,
            self_control=agent.internal_state.self_control_resource,
            alcohol_addiction_level=alcohol_state.stock,
            alcohol_tolerance=alcohol_state.tolerance_level,
            alcohol_withdrawal=alcohol_state.withdrawal_severity,
            time_since_last_drink=alcohol_state.time_since_last_use,
            gambling_habit_strength=agent.habit_stocks[BehaviorType.GAMBLING],
            gambling_total_winnings=agent.gambling_context.total_wins,
            actions_taken_this_month=agent.action_budget.actions_taken,
            time_budget_remaining=agent.action_budget.remaining_hours,
            employment_info=employment_info,
            housing_info=housing_info,
            recent_gambling_outcomes=list(agent.gambling_context.recent_outcomes)
        )

        return snapshot


@dataclass
class ActionRecord:
    """Record of a single action taken by an agent."""
    timestamp: datetime
    action_type: ActionType
    target_location: Optional[PlotID]
    target_building: Optional[BuildingID]

    # Pre-action state
    pre_wealth: float
    pre_stress: float
    pre_mood: float

    # Action details
    time_cost: float

    # Outcome
    success: bool

    # Post-action state changes (with defaults)
    wealth_change: float = 0.0
    stress_change: float = 0.0
    mood_change: float = 0.0
    addiction_change: float = 0.0

    # Fields with complex defaults (must come last)
    decision_factors: Dict[str, float] = field(default_factory=dict)
    available_alternatives: List[ActionType] = field(default_factory=list)
    outcome_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to strings
        data['action_type'] = self.action_type.value if hasattr(self.action_type, 'value') else str(self.action_type)
        data['available_alternatives'] = [
            a.value if hasattr(a, 'value') else str(a)
            for a in self.available_alternatives
        ]
        return data


@dataclass
class LifeEvent:
    """Significant life event for an agent."""
    timestamp: datetime
    event_type: EventType
    description: str

    # Event details
    details: Dict[str, Any] = field(default_factory=dict)

    # Impact on agent
    wealth_impact: float = 0.0
    stress_impact: float = 0.0
    mood_impact: float = 0.0

    # Related entities
    related_building: Optional[BuildingID] = None
    related_agent: Optional[AgentID] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data


@dataclass
class AgentHistory:
    """Complete history for a single agent."""
    agent_id: AgentID
    creation_time: datetime

    # Static characteristics
    personality_traits: PersonalityTraits
    initial_wealth: float
    initial_location: Optional[PlotID]

    # State history
    state_snapshots: List[StateSnapshot] = field(default_factory=list)
    snapshot_interval: int = 10  # Take snapshot every N actions

    # Action history
    action_records: List[ActionRecord] = field(default_factory=list)

    # Life events
    life_events: List[LifeEvent] = field(default_factory=list)

    # Summary statistics
    total_actions: int = 0
    total_months_survived: int = 0
    peak_wealth: float = 0.0
    lowest_wealth: float = float('inf')

    def add_state_snapshot(self, snapshot: StateSnapshot) -> None:
        """Add a state snapshot to history."""
        self.state_snapshots.append(snapshot)

        # Update summary stats
        if snapshot.wealth > self.peak_wealth:
            self.peak_wealth = snapshot.wealth
        if snapshot.wealth < self.lowest_wealth:
            self.lowest_wealth = snapshot.wealth

    def add_action_record(self, record: ActionRecord) -> None:
        """Add an action record to history."""
        self.action_records.append(record)
        self.total_actions += 1

    def add_life_event(self, event: LifeEvent) -> None:
        """Add a life event to history."""
        self.life_events.append(event)

    def get_state_trajectory(self, attribute: str) -> List[Tuple[datetime, float]]:
        """
        Get time series of a specific state attribute.

        Args:
            attribute: Name of attribute (e.g., 'wealth', 'stress')

        Returns:
            List of (timestamp, value) tuples
        """
        trajectory = []
        for snapshot in self.state_snapshots:
            if hasattr(snapshot, attribute):
                value = getattr(snapshot, attribute)
                trajectory.append((snapshot.timestamp, value))
        return trajectory

    def get_action_sequence(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ActionRecord]:
        """Get sequence of actions within time range."""
        actions = self.action_records

        if start_time:
            actions = [a for a in actions if a.timestamp >= start_time]
        if end_time:
            actions = [a for a in actions if a.timestamp <= end_time]

        return actions

    def to_dict(self) -> Dict[str, Any]:
        """Convert complete history to dictionary."""
        return {
            'agent_id': self.agent_id,
            'creation_time': self.creation_time.isoformat(),
            'personality_traits': asdict(self.personality_traits),
            'initial_wealth': self.initial_wealth,
            'initial_location': self.initial_location,
            'state_snapshots': [s.to_dict() for s in self.state_snapshots],
            'action_records': [a.to_dict() for a in self.action_records],
            'life_events': [e.to_dict() for e in self.life_events],
            'total_actions': self.total_actions,
            'total_months_survived': self.total_months_survived,
            'peak_wealth': self.peak_wealth,
            'lowest_wealth': self.lowest_wealth
        }


class HistoryTracker:
    """
    Central history tracking system.
    Manages detailed history recording for all agents.
    """

    def __init__(self, max_history_size: Optional[int] = None):
        """
        Initialize history tracker.

        Args:
            max_history_size: Maximum records to keep per agent (None = unlimited)
        """
        self.max_history_size = max_history_size
        self.agent_histories: Dict[AgentID, AgentHistory] = {}

        # Track current month for monthly summaries
        self.current_month = 0

        # Action tracking for snapshot triggers
        self.actions_since_snapshot: Dict[AgentID, int] = {}

    def register_agent(self, agent: Agent, timestamp: datetime) -> None:
        """
        Register a new agent for history tracking.

        Args:
            agent: Agent to track
            timestamp: Registration time
        """
        history = AgentHistory(
            agent_id=agent.id,
            creation_time=timestamp,
            personality_traits=agent.personality,
            initial_wealth=agent.internal_state.wealth,
            initial_location=agent.current_location
        )

        # Take initial snapshot
        initial_snapshot = StateSnapshot.from_agent(agent, timestamp)
        history.add_state_snapshot(initial_snapshot)

        self.agent_histories[agent.id] = history
        self.actions_since_snapshot[agent.id] = 0

    def record_action(
        self,
        agent: Agent,
        action: Action,
        outcome: ActionOutcome,
        timestamp: datetime,
        pre_state: InternalState,
        available_actions: List[Action]
    ) -> None:
        """
        Record an action taken by an agent.

        Args:
            agent: Agent who took action
            action: Action taken
            outcome: Outcome of action
            timestamp: When action occurred
            pre_state: Agent state before action
            available_actions: What alternatives were available
        """
        if agent.id not in self.agent_histories:
            return

        history = self.agent_histories[agent.id]

        # Create action record
        record = ActionRecord(
            timestamp=timestamp,
            action_type=action.action_type,
            target_location=action.target,
            target_building=action.building_id if hasattr(action, 'building_id') else None,
            pre_wealth=pre_state.wealth,
            pre_stress=pre_state.stress,
            pre_mood=pre_state.mood,
            time_cost=action.time_cost,
            decision_factors=action.utility_components if hasattr(action, 'utility_components') else {},
            available_alternatives=[a.action_type for a in available_actions],
            success=outcome.success,
            outcome_details=outcome.details,
            wealth_change=agent.internal_state.wealth - pre_state.wealth,
            stress_change=agent.internal_state.stress - pre_state.stress,
            mood_change=agent.internal_state.mood - pre_state.mood
        )

        history.add_action_record(record)

        # Check if we need a new snapshot
        self.actions_since_snapshot[agent.id] += 1
        if self.actions_since_snapshot[agent.id] >= history.snapshot_interval:
            snapshot = StateSnapshot.from_agent(agent, timestamp)
            history.add_state_snapshot(snapshot)
            self.actions_since_snapshot[agent.id] = 0

        # Enforce history size limit if set
        if self.max_history_size:
            if len(history.action_records) > self.max_history_size:
                history.action_records = history.action_records[-self.max_history_size:]

    def record_life_event(
        self,
        agent_id: AgentID,
        event_type: EventType,
        description: str,
        timestamp: datetime,
        **kwargs
    ) -> Optional[LifeEvent]:
        """
        Record a significant life event.

        Args:
            agent_id: ID of agent experiencing event
            event_type: Type of event
            description: Human-readable description
            timestamp: When event occurred
            **kwargs: Additional event details
        Returns:
            The created LifeEvent if the agent is tracked, otherwise None
        """
        if agent_id not in self.agent_histories:
            return None

        event = LifeEvent(
            timestamp=timestamp,
            event_type=event_type,
            description=description,
            details=kwargs.get('details', {}),
            wealth_impact=kwargs.get('wealth_impact', 0.0),
            stress_impact=kwargs.get('stress_impact', 0.0),
            mood_impact=kwargs.get('mood_impact', 0.0),
            related_building=kwargs.get('related_building'),
            related_agent=kwargs.get('related_agent')
        )

        self.agent_histories[agent_id].add_life_event(event)
        return event

    def detect_life_events(
        self,
        agent: Agent,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        timestamp: datetime
    ) -> List[LifeEvent]:
        """
        Detect life events by comparing pre and post states.

        Args:
            agent: Agent to check
            pre_state: State before action
            post_state: State after action
            timestamp: Current time

        Returns:
            List of detected events
        """
        events = []

        # Employment changes
        if not pre_state.get('employed') and post_state.get('employed'):
            event = self.record_life_event(
                agent.id,
                EventType.JOB_GAINED,
                f"Found employment at {post_state.get('employer_name', 'unknown')}",
                timestamp,
                details={'employer': post_state.get('employer_id')},
                wealth_impact=post_state.get('salary', 0),
                stress_impact=-0.2
            )
            if event:
                events.append(event)

        elif pre_state.get('employed') and not post_state.get('employed'):
            event = self.record_life_event(
                agent.id,
                EventType.JOB_LOST,
                "Lost employment",
                timestamp,
                wealth_impact=-pre_state.get('salary', 0),
                stress_impact=0.3
            )
            if event:
                events.append(event)

        # Housing changes
        if not pre_state.get('housed') and post_state.get('housed'):
            event = self.record_life_event(
                agent.id,
                EventType.HOUSING_GAINED,
                "Found housing",
                timestamp,
                details={'rent': post_state.get('rent', 0)},
                stress_impact=-0.3
            )
            if event:
                events.append(event)

        elif pre_state.get('housed') and not post_state.get('housed'):
            if post_state.get('evicted'):
                event = self.record_life_event(
                    agent.id,
                    EventType.EVICTED,
                    "Evicted from housing",
                    timestamp,
                    stress_impact=0.5
                )
                if event:
                    events.append(event)
            else:
                event = self.record_life_event(
                    agent.id,
                    EventType.HOUSING_LOST,
                    "Lost housing",
                    timestamp,
                    stress_impact=0.4
                )
                if event:
                    events.append(event)

        # Financial events
        wealth_change = post_state.get('wealth', 0) - pre_state.get('wealth', 0)
        if wealth_change > pre_state.get('wealth', 1) * 0.5:  # 50% wealth increase
            event = self.record_life_event(
                agent.id,
                EventType.WINDFALL,
                f"Large financial gain of ${wealth_change:.2f}",
                timestamp,
                wealth_impact=wealth_change,
                mood_impact=0.3
            )
            if event:
                events.append(event)

        elif post_state.get('wealth', 0) < 0 and pre_state.get('wealth', 0) >= 0:
            event = self.record_life_event(
                agent.id,
                EventType.BANKRUPT,
                "Went bankrupt",
                timestamp,
                stress_impact=0.5,
                mood_impact=-0.4
            )
            if event:
                events.append(event)

        # Addiction events
        alcohol_level = post_state.get('alcohol_addiction_level', 0)
        prev_alcohol = pre_state.get('alcohol_addiction_level', 0)

        if alcohol_level > 0.5 and prev_alcohol <= 0.5:
            event = self.record_life_event(
                agent.id,
                EventType.ADDICTION_ONSET,
                "Developed alcohol addiction",
                timestamp,
                details={'addiction_level': alcohol_level}
            )
            if event:
                events.append(event)

        return events

    def get_agent_history(self, agent_id: AgentID) -> Optional[AgentHistory]:
        """Get complete history for an agent."""
        return self.agent_histories.get(agent_id)

    def get_all_histories(self) -> Dict[AgentID, AgentHistory]:
        """Get histories for all agents."""
        return self.agent_histories.copy()

    def advance_month(self) -> None:
        """Called when simulation advances to next month."""
        self.current_month += 1

        # Update month counts for all agents
        for history in self.agent_histories.values():
            history.total_months_survived = self.current_month

    def get_population_trajectories(
        self,
        attribute: str,
        agent_ids: Optional[List[AgentID]] = None
    ) -> Dict[AgentID, List[Tuple[datetime, float]]]:
        """
        Get trajectories for multiple agents.

        Args:
            attribute: State attribute to track
            agent_ids: Specific agents (None = all)

        Returns:
            Dict mapping agent IDs to trajectories
        """
        if agent_ids is None:
            agent_ids = list(self.agent_histories.keys())

        trajectories = {}
        for agent_id in agent_ids:
            if agent_id in self.agent_histories:
                history = self.agent_histories[agent_id]
                trajectories[agent_id] = history.get_state_trajectory(attribute)

        return trajectories

    def clear_old_records(self, cutoff_date: datetime) -> None:
        """Remove records older than cutoff date to save memory."""
        for history in self.agent_histories.values():
            # Filter snapshots
            history.state_snapshots = [
                s for s in history.state_snapshots
                if s.timestamp >= cutoff_date
            ]

            # Filter action records
            history.action_records = [
                a for a in history.action_records
                if a.timestamp >= cutoff_date
            ]

            # Filter life events
            history.life_events = [
                e for e in history.life_events
                if e.timestamp >= cutoff_date
            ]
