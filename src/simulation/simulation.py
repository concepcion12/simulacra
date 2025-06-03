"""
Main simulation class implementing Phase 5.1 time management.
"""
from typing import List, Dict, Optional, Any, Callable
import logging
from dataclasses import dataclass

from src.agents.agent import Agent
from src.agents.decision_making import generate_available_actions, ActionContext
from src.environment.city import City
from src.environment.cues import CueGenerator
from src.agents.movement import MovementSystem
from .time_manager import TimeManager, TimeEvent, MonthlyStats


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters."""
    max_months: int = 12
    rounds_per_month: int = 10
    max_agents: int = 100
    enable_logging: bool = True
    log_level: str = "INFO"

 
class Simulation:
    """
    Main simulation class implementing monthly cycles with action rounds.
    
    Integrates all simulation components:
    - Time management with monthly cycles
    - Agent population management
    - Environment interaction
    - Action execution and outcomes
    - Data collection and statistics
    """
    
    def __init__(
        self,
        city: City,
        config: Optional[SimulationConfig] = None
    ):
        """
        Initialize the simulation.
        
        Args:
            city: The city environment
            config: Simulation configuration
        """
        self.config = config or SimulationConfig()
        
        # Core components
        self.city = city
        self.time_manager = TimeManager()
        self.agents: List[Agent] = []
        
        # Environment systems
        self.cue_generator = CueGenerator()
        self.movement_system = MovementSystem(city)
        
        # Simulation state
        self.is_running = False
        self.months_completed = 0
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Configure time manager
        self.time_manager.set_rounds_per_month(self.config.rounds_per_month)
        
        # Register event handlers
        self._register_event_handlers()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        if self.config.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
    def _register_event_handlers(self) -> None:
        """Register handlers for time-based events."""
        self.time_manager.add_event_handler(
            TimeEvent.MONTH_START,
            self._handle_month_start
        )
        self.time_manager.add_event_handler(
            TimeEvent.MONTH_END,
            self._handle_month_end
        )
        
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the simulation.
        
        Args:
            agent: Agent to add
        """
        if len(self.agents) >= self.config.max_agents:
            raise ValueError(f"Maximum agent limit ({self.config.max_agents}) reached")
            
        self.agents.append(agent)
        self.time_manager.register_agent(agent.id)
        self.logger.info(f"Added agent {agent.id} to simulation")
        
    def add_agents(self, agents: List[Agent]) -> None:
        """Add multiple agents to the simulation."""
        for agent in agents:
            self.add_agent(agent)
            
    def remove_agent(self, agent: Agent) -> None:
        """
        Remove an agent from the simulation.
        
        Args:
            agent: Agent to remove
        """
        if agent in self.agents:
            self.agents.remove(agent)
            self.time_manager.unregister_agent(agent.id)
            self.logger.info(f"Removed agent {agent.id} from simulation")
            
    def run(self) -> List[MonthlyStats]:
        """
        Run the full simulation.
        
        Returns:
            List of monthly statistics from the simulation
        """
        self.logger.info(
            f"Starting simulation with {len(self.agents)} agents for {self.config.max_months} months"
        )
        
        self.is_running = True
        
        try:
            while self.months_completed < self.config.max_months and self.is_running:
                self._run_single_month()
                self.months_completed += 1
                
        except KeyboardInterrupt:
            self.logger.info("Simulation interrupted by user")
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
            raise
        finally:
            self.is_running = False
            
        self.logger.info(f"Simulation completed after {self.months_completed} months")
        return self.time_manager.get_monthly_statistics()
        
    def run_single_month(self) -> MonthlyStats:
        """
        Run a single month of simulation.
        
        Returns:
            Statistics for the completed month
        """
        self._run_single_month()
        return self.time_manager.get_current_month_stats()
        
    def _run_single_month(self) -> None:
        """Internal method to run a single month."""
        # Start new month
        self.time_manager.start_new_month(self.agents)
        
        # Run action rounds
        month_continues = True
        while month_continues and self.is_running:
            month_continues = self._run_action_round()
            
    def _run_action_round(self) -> bool:
        """
        Run a single action round.
        
        Returns:
            True if month should continue, False if month is complete
        """
        # Advance to next round
        month_continues = self.time_manager.advance_action_round(self.agents)
        
        if not month_continues:
            return False
            
        # Process agents in random order for fairness
        import random
        agent_order = self.agents.copy()
        random.shuffle(agent_order)
        
        # Each agent takes one action this round
        for agent in agent_order:
            if not self.is_running:
                break
                
            self._process_agent_turn(agent)
            
        return True
        
    def _process_agent_turn(self, agent: Agent) -> None:
        """
        Process a single agent's turn in the action round.
        
        Args:
            agent: Agent taking their turn
        """
        try:
            # Generate environmental cues
            current_time = self.time_manager.current_time
            cues = self.cue_generator.generate_cues_for_agent(agent, self.city, current_time)
            agent.process_environmental_cues(cues)
            
            # Generate available actions
            context = ActionContext(
                agent=agent,
                environment=self.city,
                time_budget=self.time_manager.get_round_time_budget(),
                movement_system=self.movement_system
            )
            
            available_actions = generate_available_actions(agent, context)
            
            if not available_actions:
                self.logger.debug(f"No available actions for agent {agent.id}")
                return
                
            # Agent makes decision
            chosen_action = agent.make_decision(available_actions, context)
            
            # Execute action
            outcome = agent.execute_action(chosen_action, context)
            
            # Record outcome for statistics
            self.time_manager.record_action_outcome(agent.id, outcome)
            
            self.logger.debug(
                f"Agent {agent.id} executed {chosen_action.action_type} "
                f"(cost: {chosen_action.time_cost:.1f}h, success: {outcome.success})"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing agent {agent.id}: {e}")
            
    def _handle_month_start(
        self,
        event_type: TimeEvent,
        agents: List[Agent],
        time_manager: TimeManager
    ) -> None:
        """Handle month start events."""
        self.logger.info(f"Month {time_manager.current_time.month} started")
        
        # Update economic conditions at month start
        self.city.global_economy.update_monthly(self.city)
        
        # Log economic conditions
        job_conditions = self.city.global_economy.get_job_market_conditions()
        housing_conditions = self.city.global_economy.get_housing_market_conditions()
        self.logger.info(
            f"Economic conditions - Job market: {job_conditions:.2f}, "
            f"Housing market: {housing_conditions:.2f}"
        )
        
    def _handle_month_end(
        self,
        event_type: TimeEvent,
        agents: List[Agent],
        time_manager: TimeManager
    ) -> None:
        """Handle month end events."""
        self.logger.info(f"Month {time_manager.current_time.month} ended")
        
        # Log monthly summary
        stats = time_manager.get_current_month_stats()
        self.logger.info(
            f"Monthly summary: {stats.total_actions} actions, "
            f"${stats.total_salaries_paid:.0f} salaries, "
            f"${stats.total_rent_collected:.0f} rent, "
            f"{stats.agents_evicted} evictions, {stats.agents_lost_jobs} job losses"
        )
        
        # Log economic summary
        econ_summary = self.city.global_economy.get_economic_summary()
        self.logger.info(
            f"Economic indicators - Unemployment: {econ_summary['indicators']['unemployment_rate']:.1%}, "
            f"Inflation: {econ_summary['indicators']['inflation_rate']:.1%}, "
            f"Consumer confidence: {econ_summary['indicators']['consumer_confidence']:.2f}"
        )
        
    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False
        self.logger.info("Simulation stop requested")
        
    def get_simulation_state(self) -> Dict[str, Any]:
        """
        Get current simulation state information.
        
        Returns:
            Dictionary with simulation state data
        """
        return {
            'is_running': self.is_running,
            'months_completed': self.months_completed,
            'total_agents': len(self.agents),
            'time_info': self.time_manager.get_current_time_info(),
            'current_stats': self.time_manager.get_current_month_stats().__dict__
        }
        
    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about all agents.
        
        Returns:
            Dictionary with agent statistics
        """
        if not self.agents:
            return {'total_agents': 0}
            
        # Calculate aggregate statistics
        total_wealth = sum(agent.internal_state.wealth for agent in self.agents)
        avg_wealth = total_wealth / len(self.agents)
        
        employed_agents = sum(1 for agent in self.agents if agent.employment is not None)
        housed_agents = sum(1 for agent in self.agents if agent.home is not None)
        
        avg_stress = sum(agent.internal_state.stress for agent in self.agents) / len(self.agents)
        avg_mood = sum(agent.internal_state.mood for agent in self.agents) / len(self.agents)
        
        return {
            'total_agents': len(self.agents),
            'employed_agents': employed_agents,
            'employment_rate': employed_agents / len(self.agents),
            'housed_agents': housed_agents,
            'housing_rate': housed_agents / len(self.agents),
            'total_wealth': total_wealth,
            'average_wealth': avg_wealth,
            'average_stress': avg_stress,
            'average_mood': avg_mood
        }
        
    def add_event_handler(self, event_type: TimeEvent, handler: Callable) -> None:
        """
        Add a custom event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function
        """
        self.time_manager.add_event_handler(event_type, handler)
        
    def get_monthly_statistics(self) -> List[MonthlyStats]:
        """Get all historical monthly statistics."""
        return self.time_manager.get_monthly_statistics()
        
    def __repr__(self) -> str:
        return (
            f"Simulation(agents={len(self.agents)}, "
            f"months_completed={self.months_completed}, "
            f"running={self.is_running})"
        ) 