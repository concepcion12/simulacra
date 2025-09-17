"""
Time management system for Simulacra simulation.

Implements Phase 5.1 requirements:
- Monthly simulation cycle
- Action round system within months  
- Start/end of month events (rent, salary)
- Time progression mechanics
"""
from typing import List, Dict, Callable, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

from simulacra.utils.types import (
    SimulationTime, AgentID, ActionOutcome, WorkOutcome
)


class TimeEvent(Enum):
    """Types of time-based events."""
    MONTH_START = auto()
    MONTH_END = auto()
    SALARY_PAYMENT = auto()
    RENT_DUE = auto()
    ADDICTION_WITHDRAWAL = auto()
    HABIT_DECAY = auto()
    STATE_RECOVERY = auto()


@dataclass
class ScheduledEvent:
    """An event scheduled to occur at a specific time."""
    event_type: TimeEvent
    target_agent: Optional[AgentID] = None
    data: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None


@dataclass
class MonthlyStats:
    """Statistics for a completed month."""
    month: int
    year: int
    total_actions: int = 0
    total_work_hours: float = 0.0
    total_drinking_sessions: int = 0
    total_gambling_sessions: int = 0
    total_rent_collected: float = 0.0
    total_salaries_paid: float = 0.0
    agents_gained_jobs: int = 0
    agents_lost_jobs: int = 0
    agents_found_housing: int = 0
    agents_evicted: int = 0


class TimeManager:
    """
    Manages simulation time, events, and monthly cycles.
    
    Responsible for:
    - Advancing simulation time
    - Managing action rounds within months
    - Triggering start/end of month events
    - Coordinating agent time budgets
    - Tracking simulation statistics
    """
    
    def __init__(self):
        """Initialize the time manager."""
        self.current_time = SimulationTime()
        
        # Action round management
        self.current_round = 0
        self.max_rounds_per_month = 10  # Configurable
        self.action_round_hours = 28.0  # 280 total hours / 10 rounds
        
        # Event system
        self.scheduled_events: List[ScheduledEvent] = []
        self.event_handlers: Dict[TimeEvent, List[Callable]] = {
            event_type: [] for event_type in TimeEvent
        }
        
        # Statistics
        self.monthly_stats: List[MonthlyStats] = []
        self.current_month_stats = MonthlyStats(
            month=self.current_time.month,
            year=self.current_time.year
        )
        
        # Agent tracking
        self.active_agents: Set[AgentID] = set()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    def register_agent(self, agent_id: AgentID) -> None:
        """Register an agent with the time manager."""
        self.active_agents.add(agent_id)
        self.logger.info(f"Registered agent {agent_id}")
        
    def unregister_agent(self, agent_id: AgentID) -> None:
        """Unregister an agent from the time manager."""
        self.active_agents.discard(agent_id)
        self.logger.info(f"Unregistered agent {agent_id}")
        
    def add_event_handler(self, event_type: TimeEvent, handler: Callable) -> None:
        """Add an event handler for a specific event type."""
        self.event_handlers[event_type].append(handler)
        
    def schedule_event(self, event: ScheduledEvent) -> None:
        """Schedule an event to be processed."""
        self.scheduled_events.append(event)
        
    def start_new_month(self, agents: List[Any]) -> None:
        """
        Start a new month with all initialization events.
        
        Args:
            agents: List of all agents in the simulation
        """
        self.logger.info(f"Starting month {self.current_time.month}, year {self.current_time.year}")
        
        # Reset round counter
        self.current_round = 0
        
        # Reset agent action budgets
        for agent in agents:
            agent.action_budget.reset()
            self.logger.debug(f"Reset action budget for agent {agent.id}")
            
        # Update agent internal states for new month
        for agent in agents:
            agent.update_internal_states(delta_time=1)
            
        # Process month start events
        self._trigger_event(TimeEvent.MONTH_START, agents)
        
        # Schedule recurring monthly events
        self._schedule_monthly_events(agents)
        
    def advance_action_round(self, agents: List[Any]) -> bool:
        """
        Advance to the next action round within the month.
        
        Args:
            agents: List of all agents in the simulation
            
        Returns:
            True if month should continue, False if month is complete
        """
        self.current_round += 1
        
        self.logger.info(
            f"Starting action round {self.current_round}/{self.max_rounds_per_month} "
            f"(Month {self.current_time.month}, Year {self.current_time.year})"
        )
        
        # Process any scheduled events for this round
        self._process_scheduled_events(agents)
        
        # Check if month is complete
        if self.current_round >= self.max_rounds_per_month:
            self._end_current_month(agents)
            return False
            
        return True
        
    def end_current_month(self, agents: List[Any]) -> None:
        """
        End the current month and prepare for the next.
        
        Args:
            agents: List of all agents in the simulation
        """
        self._end_current_month(agents)
        
    def _end_current_month(self, agents: List[Any]) -> None:
        """Internal method to handle month end processing."""
        self.logger.info(f"Ending month {self.current_time.month}, year {self.current_time.year}")
        
        # Process end of month events
        self._trigger_event(TimeEvent.MONTH_END, agents)
        
        # Handle monthly payments and obligations
        self._process_monthly_payments(agents)
        
        # Save monthly statistics
        self.monthly_stats.append(self.current_month_stats)
        
        # Advance time
        self.current_time.advance()
        
        # Initialize new month stats
        self.current_month_stats = MonthlyStats(
            month=self.current_time.month,
            year=self.current_time.year
        )
        
    def _schedule_monthly_events(self, agents: List[Any]) -> None:
        """Schedule recurring events for the month."""
        # Schedule rent payments for mid-month (round 5)
        mid_month_round = self.max_rounds_per_month // 2
        if self.current_round < mid_month_round:
            rent_event = ScheduledEvent(
                event_type=TimeEvent.RENT_DUE,
                data={'target_round': mid_month_round}
            )
            self.schedule_event(rent_event)
            
        # Schedule salary payments for end of month
        salary_event = ScheduledEvent(
            event_type=TimeEvent.SALARY_PAYMENT,
            data={'target_round': self.max_rounds_per_month - 1}
        )
        self.schedule_event(salary_event)
        
    def _process_scheduled_events(self, agents: List[Any]) -> None:
        """Process events scheduled for the current round."""
        events_to_process = []
        remaining_events = []
        
        for event in self.scheduled_events:
            target_round = event.data.get('target_round')
            if target_round is None or target_round == self.current_round:
                events_to_process.append(event)
            else:
                remaining_events.append(event)
                
        self.scheduled_events = remaining_events
        
        # Process events
        for event in events_to_process:
            self._process_event(event, agents)
            
    def _process_event(self, event: ScheduledEvent, agents: List[Any]) -> None:
        """Process a single scheduled event."""
        if event.event_type == TimeEvent.RENT_DUE:
            self._process_rent_payments(agents)
        elif event.event_type == TimeEvent.SALARY_PAYMENT:
            self._process_salary_payments(agents)
        elif event.callback:
            event.callback(event, agents)
            
        # Trigger event handlers
        self._trigger_event(event.event_type, agents)
        
    def _process_monthly_payments(self, agents: List[Any]) -> None:
        """Process all monthly financial obligations."""
        # Handle any rent payments that might have been missed
        self._process_rent_payments(agents)

        # Pay outstanding salaries for employed agents
        self._process_salary_payments(agents)
        
    def _process_rent_payments(self, agents: List[Any]) -> None:
        """Process rent payments for all agents."""
        self.logger.info("Processing rent payments")
        
        for agent in agents:
            if agent.home is not None:
                rent_amount = agent.home.monthly_rent
                
                if agent.internal_state.wealth >= rent_amount:
                    agent.internal_state.wealth -= rent_amount
                    self.current_month_stats.total_rent_collected += rent_amount
                    
                    # Update housing tenure
                    agent.home.months_at_residence += 1
                    
                    self.logger.debug(f"Agent {agent.id} paid rent: ${rent_amount:.2f}")
                else:
                    # Handle eviction
                    self._handle_eviction(agent)
                    
    def _process_salary_payments(self, agents: List[Any]) -> None:
        """Process salary payments for employed agents."""
        self.logger.info("Processing salary payments")
        
        for agent in agents:
            if agent.employment is not None:
                # Calculate salary based on performance and base pay
                performance_avg = agent.employment.performance_history.average_performance
                base_salary = agent.employment.base_salary
                actual_salary = base_salary * performance_avg
                
                # Pay salary
                agent.internal_state.wealth += actual_salary
                self.current_month_stats.total_salaries_paid += actual_salary
                
                # Update employment tenure
                agent.employment.performance_history.months_employed += 1
                
                self.logger.debug(
                    f"Agent {agent.id} received salary: ${actual_salary:.2f} "
                    f"(performance: {performance_avg:.2f})"
                )
                
                # Check for job loss due to poor performance
                if agent.employment.performance_history.warnings_received >= 3:
                    self._handle_job_loss(agent)
                    
    def _handle_eviction(self, agent: Any) -> None:
        """Handle agent eviction due to inability to pay rent."""
        self.logger.info(f"Agent {agent.id} evicted for non-payment")
        
        # Remove housing
        agent.home = None
        agent.current_location = None  # Will need to find new location
        
        # Increase stress significantly
        agent.internal_state.stress = min(1.0, agent.internal_state.stress + 0.4)
        
        # Negative mood impact
        agent.internal_state.mood = max(-1.0, agent.internal_state.mood - 0.4)
        
        # Update statistics
        self.current_month_stats.agents_evicted += 1
        
    def _handle_job_loss(self, agent: Any) -> None:
        """Handle agent losing their job due to poor performance."""
        self.logger.info(f"Agent {agent.id} lost job due to poor performance")
        
        # Remove employment
        agent.employment = None
        
        # Increase stress
        agent.internal_state.stress = min(1.0, agent.internal_state.stress + 0.3)
        
        # Negative mood impact
        agent.internal_state.mood = max(-1.0, agent.internal_state.mood - 0.2)
        
        # Update statistics
        self.current_month_stats.agents_lost_jobs += 1
        
    def _trigger_event(self, event_type: TimeEvent, agents: List[Any], *_, **__) -> None:
        """Trigger all handlers for a specific event type."""
        for handler in self.event_handlers[event_type]:
            try:
                handler(event_type, agents, self)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_type}: {e}")
                
    def record_action_outcome(self, agent_id: AgentID, outcome: ActionOutcome) -> None:
        """Record an action outcome for statistics."""
        self.current_month_stats.total_actions += 1
        
        # Record specific action types
        if isinstance(outcome, WorkOutcome):
            # Work hours are tracked in the agent's action budget
            pass
        # Could extend for other outcome types
        
    def get_current_time_info(self) -> Dict[str, Any]:
        """Get current time information."""
        return {
            'month': self.current_time.month,
            'year': self.current_time.year,
            'total_months': self.current_time.total_months,
            'current_round': self.current_round,
            'max_rounds': self.max_rounds_per_month,
            'round_progress': self.current_round / self.max_rounds_per_month,
            'round_hours': self.action_round_hours
        }
        
    def get_monthly_statistics(self) -> List[MonthlyStats]:
        """Get historical monthly statistics."""
        return self.monthly_stats.copy()
        
    def get_current_month_stats(self) -> MonthlyStats:
        """Get statistics for the current month."""
        return self.current_month_stats
        
    def is_month_complete(self) -> bool:
        """Check if the current month is complete."""
        return self.current_round >= self.max_rounds_per_month
        
    def get_remaining_rounds(self) -> int:
        """Get number of rounds remaining in current month."""
        return max(0, self.max_rounds_per_month - self.current_round)
        
    def get_round_time_budget(self) -> float:
        """Get the time budget for each action round."""
        return self.action_round_hours
        
    def set_rounds_per_month(self, rounds: int) -> None:
        """Configure the number of action rounds per month."""
        if rounds > 0:
            self.max_rounds_per_month = rounds
            self.action_round_hours = 280.0 / rounds  # Total monthly hours / rounds
            self.logger.info(f"Set rounds per month to {rounds} ({self.action_round_hours:.1f} hours each)")
        else:
            raise ValueError("Rounds per month must be positive")
            
    def __repr__(self) -> str:
        return (
            f"TimeManager(month={self.current_time.month}, year={self.current_time.year}, "
            f"round={self.current_round}/{self.max_rounds_per_month})"
        ) 
