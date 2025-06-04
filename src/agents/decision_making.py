"""
Decision-making system implementing multi-component utility evaluation and action selection.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from src.utils.types import (
    ActionType, ActionCost, UtilityWeights, 
    BehaviorType, SubstanceType, ActionOutcome,
    PersonalityTraits, InternalState
)
from src.agents.action_outcomes import OutcomeContext
from .behavioral_economics import (
    ProspectTheoryModule,
    TemporalDiscountingModule, 
    HabitFormationModule,
    AddictionModule,
    GamblingBiasModule,
    DualProcessModule
)

if TYPE_CHECKING:
    from .movement import MovementSystem


@dataclass
class Action:
    """Represents a possible action an agent can take."""
    action_type: ActionType
    time_cost: float
    target: Optional[Any] = None  # Could be PlotID, BuildingID, etc.
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
            
    def __repr__(self):
        return f"Action({self.action_type.name}, {self.time_cost}h)"


@dataclass
class ActionContext:
    """Context information for evaluating an action."""
    agent: 'Agent'
    environment: Optional['Environment'] = None
    available_targets: Dict[ActionType, List[Any]] = None
    current_time: Optional['SimulationTime'] = None
    time_budget: Optional[float] = None
    movement_system: Optional['MovementSystem'] = None
    
    def __post_init__(self):
        if self.available_targets is None:
            self.available_targets = {}


@dataclass
class ActionEvaluation:
    """Result of evaluating an action's utility."""
    action: Action
    system1_utility: float
    system2_utility: float
    combined_utility: float
    utility_components: Dict[str, float]
    
    def __repr__(self):
        return f"Eval({self.action.action_type.name}: {self.combined_utility:.2f})"


class UtilityCalculator:
    """Calculates multi-component utility for actions."""
    
    def __init__(self):
        self.prospect_theory = ProspectTheoryModule()
        self.temporal_discounting = TemporalDiscountingModule()
        self.habit_formation = HabitFormationModule()
        self.addiction_module = AddictionModule()
        self.gambling_bias = GamblingBiasModule()
    
    def calculate_total_utility(
        self, 
        action: Action, 
        agent: 'Agent', 
        context: ActionContext
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total utility with all components.
        
        Returns:
            Tuple of (total_utility, component_breakdown)
        """
        # Get dynamic weights based on agent state
        weights = self._calculate_state_dependent_weights(agent)
        
        # Calculate component utilities
        components = {
            'financial': self._calculate_financial_utility(action, agent, context),
            'habit': self._calculate_habit_utility(action, agent),
            'addiction': self._calculate_addiction_utility(action, agent),
            'psychological': self._calculate_psychological_utility(action, agent)
        }
        
        # Weighted sum
        total = sum(weights.__dict__[comp] * util for comp, util in components.items())
        
        return total, components
    
    def _calculate_state_dependent_weights(self, agent: 'Agent') -> UtilityWeights:
        """Calculate utility weights that change based on agent's internal state."""
        # Start with base weights
        weights = UtilityWeights()
        
        # High craving dramatically shifts weights
        max_craving = agent.get_max_craving()
        if max_craving > 0.5:
            weights.addiction *= (1 + max_craving)
            weights.financial *= 0.5
            weights.normalize()
        
        # Financial pressure
        if agent.internal_state.wealth < agent.internal_state.monthly_expenses * 0.5:
            weights.financial *= 2.0
            weights.normalize()
        
        # High stress affects multiple weights
        if agent.internal_state.stress > 0.7:
            weights.psychological *= 1.5
            weights.addiction *= 1.2  # Stress increases addiction weight
            weights.normalize()

        # For backward compatibility some tests expect a 'social' attribute
        # even though it is not part of the base UtilityWeights dataclass.
        # Provide it dynamically without modifying the class definition.
        weights.social = 0.0

        return weights
    
    def _calculate_financial_utility(
        self, 
        action: Action, 
        agent: 'Agent',
        context: ActionContext
    ) -> float:
        """Calculate financial utility component."""
        wealth = agent.internal_state.wealth
        
        # Expected financial outcome
        expected_change = 0.0
        
        if action.action_type == ActionType.WORK:
            if agent.employment:
                # Assume full month's work
                expected_change = agent.employment.job.monthly_salary
            else:
                expected_change = 0  # Can't work without job
                
        elif action.action_type == ActionType.GAMBLE:
            # Expected value is negative due to house edge
            bet_amount = min(50, wealth * 0.1)  # Bet 10% of wealth or $50
            expected_change = -bet_amount * 0.05  # 5% house edge
            
        elif action.action_type == ActionType.DRINK:
            # Cost of alcohol
            expected_change = -20  # Typical drinking session cost
            
        elif action.action_type == ActionType.BEG:
            # Small expected income
            expected_change = 30  # Typical begging income
        
        # Apply prospect theory
        future_wealth = wealth + expected_change
        value = self.prospect_theory.evaluate_outcome(
            future_wealth,
            wealth,  # Current wealth as reference point
            agent.personality
        )
        
        # Normalize to reasonable range
        return np.tanh(value / 100)  # Sigmoid-like normalization
    
    def _calculate_habit_utility(self, action: Action, agent: 'Agent') -> float:
        """Calculate utility from habit reinforcement."""
        if action.action_type == ActionType.DRINK:
            habit_stock = agent.habit_stocks.get(BehaviorType.DRINKING, 0)
            consumption = action.parameters.get('units', 2)  # Default 2 units
            
            return self.habit_formation.calculate_habit_utility(
                consumption,
                habit_stock,
                phi=0.5
            )
            
        elif action.action_type == ActionType.GAMBLE:
            habit_stock = agent.habit_stocks.get(BehaviorType.GAMBLING, 0)
            # Gambling "consumption" is time spent
            consumption = action.time_cost
            
            return self.habit_formation.calculate_habit_utility(
                consumption,
                habit_stock,
                phi=0.3  # Less sensitive than drinking
            )
        
        return 0.0
    
    def _calculate_addiction_utility(self, action: Action, agent: 'Agent') -> float:
        """Calculate utility from addiction relief."""
        if action.action_type != ActionType.DRINK:
            return 0.0
        
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        
        # Components of addiction utility
        euphoria = 0.0
        withdrawal_relief = 0.0
        craving_relief = 0.0
        
        # Expected consumption
        units = action.parameters.get('units', 2)
        
        # Euphoria (reduced by tolerance)
        base_euphoria = units * 0.3
        euphoria = self.addiction_module.calculate_tolerance_effect(
            base_euphoria,
            alcohol_state.tolerance_level
        )
        
        # Withdrawal relief
        if alcohol_state.withdrawal_severity > 0:
            withdrawal_relief = alcohol_state.withdrawal_severity * 0.8
        
        # Craving relief
        craving = agent.craving_intensities.get(SubstanceType.ALCOHOL, 0)
        if craving > 0:
            craving_relief = craving * 0.6
        
        # Shift from positive to negative reinforcement with addiction
        addiction_factor = min(1.0, alcohol_state.stock)
        
        total = (
            (1 - addiction_factor) * euphoria +
            addiction_factor * (withdrawal_relief + craving_relief)
        )
        
        return total
    
    def _calculate_psychological_utility(
        self, 
        action: Action, 
        agent: 'Agent'
    ) -> float:
        """Calculate psychological utility (mood, stress relief)."""
        mood = agent.internal_state.mood
        stress = agent.internal_state.stress
        
        utility = 0.0
        
        if action.action_type == ActionType.REST:
            # Rest reduces stress and improves mood
            stress_relief = stress * 0.3
            mood_boost = (1 - mood) * 0.2 if mood < 0.5 else 0
            utility = stress_relief + mood_boost
            
        elif action.action_type == ActionType.DRINK:
            # Temporary stress relief (but we know it's maladaptive)
            stress_relief = stress * 0.4
            utility = stress_relief
            

            
        elif action.action_type == ActionType.WORK:
            # Work increases stress (negative utility)
            if agent.employment:
                stress_increase = -agent.employment.job.stress_level * 0.3
                utility = stress_increase
                
        elif action.action_type == ActionType.GAMBLE:
            # Excitement utility (separate from financial)
            excitement = 0.2
            # But also stress if losing streak
            if hasattr(agent, 'gambling_context') and agent.gambling_context.loss_streak > 3:
                stress_penalty = -0.3
                excitement += stress_penalty
            utility = excitement
        
        return utility


class System1Evaluator:
    """Fast, intuitive evaluation of actions."""
    
    def evaluate(self, action: Action, agent: 'Agent', context: ActionContext) -> float:
        """
        Quick heuristic evaluation based on immediate appeal.
        
        Returns utility in range [-1, 1].
        """
        action_type = action.action_type
        
        if action_type == ActionType.DRINK:
            # Immediate appeal based on craving and stress
            alcohol_craving = agent.craving_intensities.get(SubstanceType.ALCOHOL, 0)
            stress = agent.internal_state.stress
            
            appeal = alcohol_craving * 2.0 + stress * 0.5
            return np.tanh(appeal)  # Normalize to [-1, 1]
            
        elif action_type == ActionType.GAMBLE:
            # Excitement and loss chasing
            gambling_craving = agent.craving_intensities.get(BehaviorType.GAMBLING, 0)
            base_appeal = 0.3 + gambling_craving
            
            # Gambler's fallacy kicks in
            if hasattr(agent, 'gambling_context') and agent.gambling_context.loss_streak > 2:
                base_appeal *= (1 + agent.personality.gambling_bias_strength * 0.5)
            
            return np.tanh(base_appeal)
            
        elif action_type == ActionType.WORK:
            # Low immediate appeal, especially when stressed
            appeal = 0.1 - agent.internal_state.stress * 0.2
            return appeal
            
        elif action_type == ActionType.REST:
            # Moderate appeal when tired/stressed
            appeal = 0.3 + agent.internal_state.cognitive_load * 0.4
            return appeal
            
        elif action_type == ActionType.BEG:
            # Low appeal unless desperate
            wealth_ratio = agent.internal_state.wealth / agent.internal_state.monthly_expenses
            if wealth_ratio < 0.2:
                appeal = 0.5  # Desperate times
            else:
                appeal = -0.3  # Aversive
            return appeal
            
        else:
            # Default neutral appeal
            return 0.0


class DecisionMaker:
    """Main decision-making system combining all components."""
    
    def __init__(self, temperature: float = 0.1):
        """
        Initialize decision maker.
        
        Args:
            temperature: Softmax temperature for action selection (lower = more deterministic)
        """
        self.utility_calculator = UtilityCalculator()
        self.system1_evaluator = System1Evaluator()
        self.dual_process = DualProcessModule()
        self.temperature = temperature
    
    def choose_action(
        self, 
        agent: 'Agent', 
        available_actions: List[Action],
        context: ActionContext
    ) -> Action:
        """
        Choose an action using dual-process evaluation and stochastic selection.
        
        Args:
            agent: The agent making the decision
            available_actions: List of possible actions
            context: Context information
            
        Returns:
            Selected action
        """
        if not available_actions:
            raise ValueError("No available actions to choose from")
        
        # Calculate effective theta (System 2 weight)
        theta_effective = self._calculate_effective_theta(agent)
        
        # Evaluate all actions
        evaluations = []
        for action in available_actions:
            evaluation = self._evaluate_action(action, agent, context, theta_effective)
            evaluations.append(evaluation)
        
        # Select action using softmax
        selected_action = self._softmax_selection(evaluations)
        
        return selected_action
    
    def _calculate_effective_theta(self, agent: 'Agent') -> float:
        """Calculate effective System 2 weight based on agent state."""
        return self.dual_process.calculate_effective_theta(
            agent.personality,
            agent.internal_state.self_control_resource,
            agent.internal_state.cognitive_load,
            agent.get_max_craving(),
            agent.internal_state.stress
        )
    
    def _evaluate_action(
        self,
        action: Action,
        agent: 'Agent',
        context: ActionContext,
        theta: float
    ) -> ActionEvaluation:
        """Evaluate a single action using dual-process framework."""
        # System 1 evaluation (fast, intuitive)
        system1_utility = self.system1_evaluator.evaluate(action, agent, context)
        
        # System 2 evaluation (slow, deliberative)
        system2_utility, components = self.utility_calculator.calculate_total_utility(
            action, agent, context
        )
        
        # Combine using theta
        combined_utility = self.dual_process.combine_system_evaluations(
            system1_utility,
            system2_utility,
            theta
        )
        
        return ActionEvaluation(
            action=action,
            system1_utility=system1_utility,
            system2_utility=system2_utility,
            combined_utility=combined_utility,
            utility_components=components
        )
    
    def _softmax_selection(self, evaluations: List[ActionEvaluation]) -> Action:
        """
        Select action using softmax (Boltzmann) distribution.
        
        Higher utility actions are more likely to be selected, but not deterministic.
        """
        # Extract utilities
        utilities = np.array([e.combined_utility for e in evaluations])
        
        # Apply temperature and compute probabilities
        # Subtract max for numerical stability
        utilities_stable = utilities - np.max(utilities)
        exp_utilities = np.exp(utilities_stable / self.temperature)
        probabilities = exp_utilities / np.sum(exp_utilities)
        
        # Sample action
        selected_idx = np.random.choice(len(evaluations), p=probabilities)
        
        return evaluations[selected_idx].action
    
    def get_action_probabilities(
        self,
        agent: 'Agent',
        available_actions: List[Action],
        context: ActionContext
    ) -> List[Tuple[Action, float]]:
        """
        Get probability distribution over actions.
        
        Useful for analysis and debugging.
        """
        theta_effective = self._calculate_effective_theta(agent)
        
        evaluations = []
        for action in available_actions:
            evaluation = self._evaluate_action(action, agent, context, theta_effective)
            evaluations.append(evaluation)
        
        # Calculate probabilities
        utilities = np.array([e.combined_utility for e in evaluations])
        utilities_stable = utilities - np.max(utilities)
        exp_utilities = np.exp(utilities_stable / self.temperature)
        probabilities = exp_utilities / np.sum(exp_utilities)
        
        return [(e.action, p) for e, p in zip(evaluations, probabilities)]


def generate_available_actions(agent: 'Agent', context: ActionContext) -> List[Action]:
    """
    Generate all available actions for an agent given their current state and context.
    
    This function checks agent state, environment, and constraints to determine
    which actions are possible.
    
    Args:
        agent: The agent to generate actions for
        context: Environmental and simulation context
        
    Returns:
        List of available actions with their calculated utilities
    """
    available_actions = []
    
    # Get location-based context
    district_wealth = 0.5
    location_quality = 0.5
    social_density = 0.5
    market_conditions = 0.5
    
    if agent.current_location and context.environment:
        plot = context.environment.get_plot(agent.current_location)
        if plot:
            district = context.environment.get_district(plot.district_id)
            if district:
                district_wealth = district.wealth_level
                
        # Get actual market conditions from economy
        if hasattr(context.environment, 'global_economy'):
            market_conditions = context.environment.global_economy.get_job_market_conditions()
    
    # Create outcome context for utility calculations
    outcome_context = OutcomeContext(
        environment=context.environment,
        district_wealth=district_wealth,
        location_quality=location_quality,
        market_conditions=market_conditions,
        social_density=social_density
    )

    # Get movement system from context (prefer direct parameter over environment)
    movement_system = context.movement_system
    if movement_system is None and context.environment and hasattr(context.environment, 'movement_system'):
        movement_system = context.environment.movement_system
    
    # Current location
    current_location = agent.current_location
    
    # Always available actions (can be done anywhere)
    if agent.action_budget.can_afford(ActionCost.REST):
        available_actions.append(Action(ActionType.REST, ActionCost.REST))
    
    # Movement to home (if agent has a home and not already there)
    if agent.home and current_location != agent.home.plot_id:
        if agent.action_budget.can_afford(ActionCost.MOVE_HOME):
            # Calculate actual movement time if movement system available
            move_time = ActionCost.MOVE_HOME
            if movement_system:
                actual_time = movement_system.calculate_movement_time(
                    current_location,
                    agent.home.plot_id,
                    agent.internal_state.stress
                )
                move_time = actual_time
            
            if agent.action_budget.can_afford(move_time):
                available_actions.append(Action(
                    ActionType.MOVE_HOME,
                    move_time,
                    target=agent.home.plot_id
                ))
    
    # Location-dependent actions
    if movement_system and current_location:
        # Work (if employed and can reach workplace)
        if agent.employment and agent.action_budget.can_afford(ActionCost.WORK):
            # Find employer location from employer_id
            work_location = None
            for plot_id, plot in movement_system.city._plot_index.items():
                if plot.building and hasattr(plot.building, 'id') and plot.building.id == agent.employment.employer_id:
                    work_location = plot_id
                    break
            
            if work_location:
                travel_time = movement_system.calculate_movement_time(
                    current_location,
                    work_location,
                    agent.internal_state.stress
                )
                total_time = ActionCost.WORK + travel_time
                
                if agent.action_budget.can_afford(total_time):
                    available_actions.append(Action(
                        ActionType.WORK,
                        total_time,
                        target=work_location
                    ))
        
        # Job search (if unemployed)
        if not agent.employment and agent.action_budget.can_afford(ActionCost.FIND_JOB):
            # Find reachable employers
            targets = movement_system.get_available_action_targets(
                current_location,
                ActionType.FIND_JOB,
                agent.action_budget.remaining_hours - ActionCost.FIND_JOB,
                agent.internal_state.stress
            )
            
            # Add action for each reachable employer
            for building_id, plot_id, travel_time in targets[:3]:  # Limit to 3 nearest
                total_time = ActionCost.FIND_JOB + travel_time
                if agent.action_budget.can_afford(total_time):
                    available_actions.append(Action(
                        ActionType.FIND_JOB,
                        total_time,
                        target=plot_id,
                        parameters={'employer_id': building_id}
                    ))
        
        # Housing search (if homeless)
        if not agent.home and agent.action_budget.can_afford(ActionCost.FIND_HOUSING):
            targets = movement_system.get_available_action_targets(
                current_location,
                ActionType.FIND_HOUSING,
                agent.action_budget.remaining_hours - ActionCost.FIND_HOUSING,
                agent.internal_state.stress
            )
            
            for building_id, plot_id, travel_time in targets[:3]:
                total_time = ActionCost.FIND_HOUSING + travel_time
                if agent.action_budget.can_afford(total_time):
                    available_actions.append(Action(
                        ActionType.FIND_HOUSING,
                        total_time,
                        target=plot_id,
                        parameters={'building_id': building_id}
                    ))
        
        # Drinking (if can afford time and money)
        if agent.internal_state.wealth > 20:
            targets = movement_system.get_available_action_targets(
                current_location,
                ActionType.DRINK,
                agent.action_budget.remaining_hours - ActionCost.DRINK,
                agent.internal_state.stress
            )
            
            for building_id, plot_id, travel_time in targets[:2]:
                total_time = ActionCost.DRINK + travel_time
                if agent.action_budget.can_afford(total_time):
                    available_actions.append(Action(
                        ActionType.DRINK,
                        total_time,
                        target=plot_id,
                        parameters={'units': 2, 'store_id': building_id}
                    ))
        
        # Gambling (if can afford time and has money to gamble)
        if agent.internal_state.wealth > 10:
            targets = movement_system.get_available_action_targets(
                current_location,
                ActionType.GAMBLE,
                agent.action_budget.remaining_hours - ActionCost.GAMBLE,
                agent.internal_state.stress
            )
            
            for building_id, plot_id, travel_time in targets[:2]:
                total_time = ActionCost.GAMBLE + travel_time
                if agent.action_budget.can_afford(total_time):
                    available_actions.append(Action(
                        ActionType.GAMBLE,
                        total_time,
                        target=plot_id,
                        parameters={'casino_id': building_id}
                    ))
        
        # Begging (public spaces)
        targets = movement_system.get_available_action_targets(
            current_location,
            ActionType.BEG,
            agent.action_budget.remaining_hours - ActionCost.BEG,
            agent.internal_state.stress
        )
        
        for building_id, plot_id, travel_time in targets[:2]:
            total_time = ActionCost.BEG + travel_time
            if agent.action_budget.can_afford(total_time):
                available_actions.append(Action(
                    ActionType.BEG,
                    total_time,
                    target=plot_id
                ))
    
    else:
        # Fallback to simplified version without movement system
        # Work (if employed)
        if agent.employment and agent.action_budget.can_afford(ActionCost.WORK):
            available_actions.append(Action(ActionType.WORK, ActionCost.WORK))
        
        # Job search (if unemployed)
        if not agent.employment and agent.action_budget.can_afford(ActionCost.FIND_JOB):
            available_actions.append(Action(ActionType.FIND_JOB, ActionCost.FIND_JOB))
        
        # Housing search (if homeless)
        if not agent.home and agent.action_budget.can_afford(ActionCost.FIND_HOUSING):
            available_actions.append(Action(ActionType.FIND_HOUSING, ActionCost.FIND_HOUSING))
        
        # Drinking (if can afford time and money)
        if agent.action_budget.can_afford(ActionCost.DRINK) and agent.internal_state.wealth > 20:
            available_actions.append(Action(
                ActionType.DRINK,
                ActionCost.DRINK,
                parameters={'units': 2}
            ))
        
        # Gambling (if can afford time and has money to gamble)
        if agent.action_budget.can_afford(ActionCost.GAMBLE) and agent.internal_state.wealth > 10:
            available_actions.append(Action(ActionType.GAMBLE, ActionCost.GAMBLE))
        
        # Begging (last resort)
        if agent.action_budget.can_afford(ActionCost.BEG):
            available_actions.append(Action(ActionType.BEG, ActionCost.BEG))
    
    return available_actions 
