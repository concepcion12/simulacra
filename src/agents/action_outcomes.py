"""
Action outcome generation and state update system.

This module implements Phase 4.1 of the roadmap:
- Outcome generation for each action type
- Stochastic elements (gambling wins/losses, begging income)  
- Outcome → state update pipeline
- Action failure handling and constraints
"""
from typing import Optional, Any, TYPE_CHECKING
import numpy as np
from dataclasses import dataclass

from src.utils.types import (
    ActionType, ActionOutcome, WorkOutcome, GamblingOutcome, DrinkingOutcome,
    BeggingOutcome, JobSearchOutcome, HousingSearchOutcome, MoveOutcome,
    RestOutcome, BehaviorType, SubstanceType,
    EmploymentInfo, HousingInfo
)

if TYPE_CHECKING:
    from .decision_making import Action
    from .agent import Agent


@dataclass
class OutcomeContext:
    """Context information for generating action outcomes."""
    environment: Optional[Any] = None  # Environment reference for location-based outcomes
    district_wealth: float = 0.5  # [0,1] wealth level of current district
    location_quality: float = 0.5  # [0,1] quality of current location
    market_conditions: float = 0.5  # [0,1] economic conditions
    social_density: float = 0.5  # [0,1] number of people around


class ActionOutcomeGenerator:
    """Generates outcomes for different action types with stochastic elements."""
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize outcome generator.
        
        Args:
            random_seed: Optional seed for reproducible outcomes
        """
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def generate_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: Optional[OutcomeContext] = None
    ) -> ActionOutcome:
        """
        Generate outcome for an action based on agent state and context.
        
        Args:
            agent: Agent performing the action
            action: Action being performed
            context: Environmental context
            
        Returns:
            Specific outcome type based on action
        """
        if context is None:
            context = OutcomeContext()
            
        # Route to specific outcome generator
        outcome_generators = {
            ActionType.WORK: self._generate_work_outcome,
            ActionType.GAMBLE: self._generate_gambling_outcome,
            ActionType.DRINK: self._generate_drinking_outcome,
            ActionType.BEG: self._generate_begging_outcome,
            ActionType.FIND_JOB: self._generate_job_search_outcome,
            ActionType.FIND_HOUSING: self._generate_housing_search_outcome,
            ActionType.MOVE_HOME: self._generate_move_outcome,
            ActionType.REST: self._generate_rest_outcome,
        }
        
        generator = outcome_generators.get(action.action_type)
        if generator is None:
            return ActionOutcome(success=False, message=f"No generator for {action.action_type}")
            
        return generator(agent, action, context)
    
    def _generate_work_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> WorkOutcome:
        """Generate work outcome based on performance and conditions."""
        if agent.employment is None:
            return WorkOutcome(
                success=False,
                message="Cannot work without employment",
                payment=0.0
            )
        
        # Base performance affected by agent state
        base_performance = 1.0
        
        # Past performance affects current performance (consistency)
        if agent.employment.performance_history.recent_performances:
            avg_performance = agent.employment.performance_history.average_performance
            base_performance = 0.7 * base_performance + 0.3 * avg_performance
        
        # Stress reduces performance
        stress_penalty = agent.internal_state.stress * 0.3
        
        # Withdrawal reduces performance significantly
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        withdrawal_penalty = alcohol_state.withdrawal_severity * 0.4
        
        # Mood affects performance
        mood_bonus = agent.internal_state.mood * 0.1
        
        # Calculate final performance
        performance = base_performance - stress_penalty - withdrawal_penalty + mood_bonus
        performance = np.clip(performance, 0.1, 1.5)  # Clamp to reasonable range
        
        # Add some randomness
        performance *= np.random.normal(1.0, 0.1)
        performance = np.clip(performance, 0.1, 1.5)
        
        # Calculate payment based on performance and job quality
        base_salary = agent.employment.base_salary
        payment = base_salary * performance * (action.time_cost / 160.0)  # Pro-rated
        
        # Stress increase from working
        stress_increase = 0.05 + np.random.normal(0, 0.02)
        stress_increase = max(0, stress_increase)
        
        # Poor performance increases stress
        if performance < 0.7:
            stress_increase += (0.7 - performance) * 0.2
        
        return WorkOutcome(
            success=True,
            payment=payment,
            performance=performance,
            stress_increase=stress_increase,
            message=f"Worked {action.time_cost:.1f}h, performance: {performance:.2f}"
        )
    
    def _generate_gambling_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> GamblingOutcome:
        """Generate gambling outcome with house edge and near-miss mechanics."""
        # Get bet amount from action parameters or default
        bet_amount = action.parameters.get('bet_amount', min(50.0, agent.internal_state.wealth * 0.1))
        
        # Base probability of winning (before house edge)
        base_win_prob = 0.45  # House edge on win probability
        
        # Apply gambling biases
        gambling_context = agent.gambling_context
        
        # Gambler's fallacy - if on losing streak, agent might think they're "due"
        if gambling_context.loss_streak >= 3:
            # This doesn't change actual odds, just affects how much they bet
            bet_amount *= (1 + gambling_context.loss_streak * 0.1)
            bet_amount = min(bet_amount, agent.internal_state.wealth)
        
        # Check if agent can afford bet
        if bet_amount > agent.internal_state.wealth:
            return GamblingOutcome(
                success=False,
                message="Insufficient funds for gambling",
                monetary_change=0.0
            )
        
        # Determine outcome
        win_roll = np.random.random()
        won = win_roll < base_win_prob
        
        # Near-miss detection (lost but close)
        near_miss_threshold = 0.1  # Within 10% of winning
        was_near_miss = (not won and 
                        win_roll < base_win_prob + near_miss_threshold)
        
        # Calculate monetary change
        if won:
            # Win roughly 2:1 payout but with house edge
            payout_ratio = np.random.uniform(1.05, 1.3)
            monetary_change = bet_amount * payout_ratio - bet_amount
            gambling_context.loss_streak = 0
        else:
            # Lose the bet
            monetary_change = -bet_amount
            gambling_context.loss_streak += 1
            gambling_context.total_losses += bet_amount
        
        # Psychological impact
        psychological_impact = 0.0
        if won:
            # Winning provides mood boost but can increase addiction
            psychological_impact = 0.3 + np.random.normal(0, 0.1)
        elif was_near_miss:
            # Near-miss creates frustration but also excitement
            psychological_impact = -0.1 + np.random.normal(0, 0.1)
        else:
            # Regular loss creates negative mood
            psychological_impact = -0.2 + np.random.normal(0, 0.1)
        
        # Update gambling context
        gambling_context.recent_outcomes.append(GamblingOutcome(
            success=True,
            monetary_change=monetary_change,
            was_near_miss=was_near_miss,
            psychological_impact=psychological_impact
        ))
        
        # Keep only recent outcomes
        if len(gambling_context.recent_outcomes) > 10:
            gambling_context.recent_outcomes.pop(0)
        
        result_text = "Won" if won else ("Near miss" if was_near_miss else "Lost")
        return GamblingOutcome(
            success=True,
            monetary_change=monetary_change,
            was_near_miss=was_near_miss,
            psychological_impact=psychological_impact,
            message=f"{result_text} ${abs(monetary_change):.2f} gambling"
        )
    
    def _generate_drinking_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> DrinkingOutcome:
        """Generate drinking outcome with cost and physiological effects."""
        # Get drinking parameters
        units = action.parameters.get('units', 2)  # Default 2 drinks
        
        # Cost varies by district wealth (richer areas more expensive)
        base_cost_per_unit = 8.0
        district_multiplier = 0.5 + context.district_wealth
        cost_per_unit = base_cost_per_unit * district_multiplier
        total_cost = units * cost_per_unit
        
        # Check if agent can afford
        if total_cost > agent.internal_state.wealth:
            # Reduce units to what they can afford
            affordable_units = int(agent.internal_state.wealth / cost_per_unit)
            if affordable_units == 0:
                return DrinkingOutcome(
                    success=False,
                    message="Cannot afford alcohol",
                    cost=0.0
                )
            units = affordable_units
            total_cost = units * cost_per_unit
        
        # Physiological effects
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        
        # Tolerance reduces effects
        tolerance_factor = 1.0 - alcohol_state.tolerance_level * 0.7
        
        # Stress relief (primary motivation for many)
        base_stress_relief = 0.3 * units * tolerance_factor
        stress_relief = base_stress_relief + np.random.normal(0, 0.1)
        stress_relief = max(0, stress_relief)
        
        # Mood change (initially positive, but can turn negative)
        if alcohol_state.stock < 0.3:
            # Low addiction - generally positive mood effect
            mood_change = 0.2 * units * tolerance_factor + np.random.normal(0, 0.1)
        else:
            # High addiction - diminished positive effects
            mood_change = 0.1 * units * tolerance_factor + np.random.normal(0, 0.15)
            # Chance of negative mood if tolerance is high
            if tolerance_factor < 0.5:
                mood_change *= np.random.uniform(0.5, 1.0)
        
        return DrinkingOutcome(
            success=True,
            cost=total_cost,
            units_consumed=units,
            stress_relief=stress_relief,
            mood_change=mood_change,
            message=f"Consumed {units} drinks for ${total_cost:.2f}"
        )
    
    def _generate_begging_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> BeggingOutcome:
        """Generate begging outcome based on location and social factors."""
        # Base income varies by location quality and district wealth
        base_income_per_hour = 5.0 * context.district_wealth * context.location_quality
        
        # Social density affects income (more people = more potential donors)
        density_multiplier = 0.5 + context.social_density * 0.8
        
        # Agent's condition affects income
        # High stress/poor mood makes people less sympathetic
        sympathy_factor = 1.0
        if agent.internal_state.stress > 0.7:
            sympathy_factor += 0.3  # People more sympathetic to obviously distressed
        if agent.internal_state.mood < -0.5:
            sympathy_factor += 0.2  # Visible sadness increases sympathy
        
        # Calculate income with randomness
        expected_income = (base_income_per_hour * action.time_cost * 
                          density_multiplier * sympathy_factor)
        
        # High variance in begging income
        income = np.random.exponential(expected_income)  # Exponential distribution for realistic skew
        income = min(income, expected_income * 3)  # Cap extreme outliers
        
        # Social cost increases with wealth of area (stigma)
        social_cost = context.district_wealth * 0.2 + np.random.normal(0, 0.05)
        social_cost = max(0, social_cost)
        
        return BeggingOutcome(
            success=True,
            income=income,
            social_cost=social_cost,
            location_quality=context.location_quality,
            message=f"Earned ${income:.2f} begging for {action.time_cost:.1f}h"
        )
    
    def _generate_job_search_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> JobSearchOutcome:
        """Generate job search outcome based on agent state and market conditions."""
        # Base probability of finding job
        base_success_prob = 0.3 * context.market_conditions
        
        # Agent factors that affect job search success
        # Stress and withdrawal reduce interview performance
        stress_penalty = agent.internal_state.stress * 0.5
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        withdrawal_penalty = alcohol_state.withdrawal_severity * 0.4
        
        # Good mood helps with interviews
        mood_bonus = max(0, agent.internal_state.mood) * 0.4
        
        # Calculate success probability
        success_prob = base_success_prob * (1 - stress_penalty - withdrawal_penalty + mood_bonus)
        success_prob = np.clip(success_prob, 0.01, 0.8)  # Realistic bounds
        
        # Check if job found
        job_found = np.random.random() < success_prob
        
        job_quality = 0.0
        stress_change = 0.1  # Job searching is stressful
        
        if job_found:
            # Quality of job found (affects salary and working conditions)
            job_quality = np.random.uniform(0.3, 0.9)  # Most jobs are decent
            job_quality += agent.internal_state.mood * 0.1  # Mood affects quality of job found
            job_quality = np.clip(job_quality, 0.1, 1.0)
            
            stress_change = -0.2  # Finding job reduces stress
        else:
            # Failed search increases stress
            stress_change += 0.1
        
        return JobSearchOutcome(
            success=True,
            job_found=job_found,
            job_quality=job_quality,
            stress_change=stress_change,
            message=f"Job search: {'Found position' if job_found else 'No opportunities'}"
        )
    
    def _generate_housing_search_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> HousingSearchOutcome:
        """Generate housing search outcome."""
        # Success probability based on wealth and market conditions
        wealth_factor = min(1.0, agent.internal_state.wealth / 2000.0)  # Need money for deposits
        success_prob = 0.2 * wealth_factor * context.market_conditions
        
        housing_found = np.random.random() < success_prob
        
        housing_quality = 0.0
        rent_cost = 0.0
        
        if housing_found:
            # Quality varies with what agent can afford
            affordable_rent = agent.internal_state.wealth * 0.3  # 30% of wealth for rent
            
            # Generate housing options based on affordability
            if affordable_rent < 500:
                housing_quality = np.random.uniform(0.1, 0.4)  # Low quality
                rent_cost = np.random.uniform(300, 500)
            elif affordable_rent < 1000:
                housing_quality = np.random.uniform(0.3, 0.7)  # Medium quality
                rent_cost = np.random.uniform(500, 1000)
            else:
                housing_quality = np.random.uniform(0.6, 0.9)  # High quality
                rent_cost = np.random.uniform(800, 1500)
        
        return HousingSearchOutcome(
            success=True,
            housing_found=housing_found,
            housing_quality=housing_quality,
            rent_cost=rent_cost,
            message=f"Housing search: {'Found place' if housing_found else 'No suitable options'}"
        )
    
    def _generate_move_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> MoveOutcome:
        """Generate moving outcome."""
        # Moving costs vary by distance and amount of stuff
        base_move_cost = 200.0
        move_cost = base_move_cost * np.random.uniform(0.8, 1.5)
        
        # Check if agent can afford move
        if move_cost > agent.internal_state.wealth:
            return MoveOutcome(
                success=False,
                message="Cannot afford moving costs",
                move_cost=0.0
            )
        
        # Moving is stressful but exciting
        stress_change = 0.1 + np.random.normal(0, 0.05)
        
        # New location is stored in action.target
        new_location = action.target
        
        return MoveOutcome(
            success=True,
            move_cost=move_cost,
            stress_change=stress_change,
            new_location=new_location,
            message=f"Moved to new location for ${move_cost:.2f}"
        )
    
    def _generate_rest_outcome(
        self, 
        agent: 'Agent', 
        action: 'Action', 
        context: OutcomeContext
    ) -> RestOutcome:
        """Generate rest outcome with recovery effects."""
        # Base recovery rates
        base_stress_reduction = 0.2
        base_mood_improvement = 0.1
        base_self_control_restoration = 0.3
        
        # Quality of rest location affects recovery
        location_multiplier = 0.5 + context.location_quality * 0.5
        
        # Agent's physical state affects recovery
        # Withdrawal makes rest less effective
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        withdrawal_penalty = alcohol_state.withdrawal_severity * 0.3
        
        # Calculate actual recovery
        stress_reduction = (base_stress_reduction * location_multiplier * 
                          (1 - withdrawal_penalty) + np.random.normal(0, 0.05))
        stress_reduction = max(0, stress_reduction)
        
        mood_improvement = (base_mood_improvement * location_multiplier * 
                          (1 - withdrawal_penalty * 0.5) + np.random.normal(0, 0.03))
        
        self_control_restoration = (base_self_control_restoration * location_multiplier * 
                                  (1 - withdrawal_penalty * 0.2) + np.random.normal(0, 0.05))
        self_control_restoration = max(0, self_control_restoration)
        
        return RestOutcome(
            success=True,
            stress_reduction=stress_reduction,
            mood_improvement=mood_improvement,
            self_control_restoration=self_control_restoration,
            message=f"Rested for {action.time_cost:.1f}h"
        )


class StateUpdater:
    """Applies action outcomes to agent state."""
    
    def apply_outcome(self, agent: 'Agent', outcome: ActionOutcome) -> None:
        """
        Apply an action outcome to update agent state.
        
        Args:
            agent: Agent to update
            outcome: Outcome to apply
        """
        # Route to specific state updater
        updaters = {
            WorkOutcome: self._apply_work_outcome,
            GamblingOutcome: self._apply_gambling_outcome,
            DrinkingOutcome: self._apply_drinking_outcome,
            BeggingOutcome: self._apply_begging_outcome,
            JobSearchOutcome: self._apply_job_search_outcome,
            HousingSearchOutcome: self._apply_housing_search_outcome,
            MoveOutcome: self._apply_move_outcome,
            RestOutcome: self._apply_rest_outcome,
        }
        
        updater = updaters.get(type(outcome))
        if updater is None:
            return  # No specific updater, skip
            
        updater(agent, outcome)
    
    def _apply_work_outcome(self, agent: 'Agent', outcome: WorkOutcome) -> None:
        """Apply work outcome to agent state."""
        if not outcome.success:
            return
            
        # Update wealth
        agent.internal_state.wealth += outcome.payment
        
        # Update stress
        agent.internal_state.stress += outcome.stress_increase
        agent.internal_state.stress = np.clip(agent.internal_state.stress, 0, 1)
        
        # Deplete self-control from work effort
        self_control_cost = 0.1 * (outcome.stress_increase / 0.05)  # More stress = more depletion
        agent.internal_state.self_control_resource -= self_control_cost
        agent.internal_state.self_control_resource = max(0, agent.internal_state.self_control_resource)
        
        # Track work performance
        if agent.employment is not None:
            agent.employment.performance_history.add_performance(outcome.performance)
            agent.employment.performance_history.months_employed += 1
    
    def _apply_gambling_outcome(self, agent: 'Agent', outcome: GamblingOutcome) -> None:
        """Apply gambling outcome to agent state."""
        if not outcome.success:
            return
            
        # Update wealth
        agent.internal_state.wealth += outcome.monetary_change
        agent.internal_state.wealth = max(0, agent.internal_state.wealth)
        
        # Update mood
        agent.internal_state.mood += outcome.psychological_impact
        agent.internal_state.mood = np.clip(agent.internal_state.mood, -1, 1)
        
        # Update habit stock
        gambling_consumption = 1.0  # One gambling session
        agent.habit_stocks[BehaviorType.GAMBLING] = agent.habit_formation.update_habit_stock(
            agent.habit_stocks[BehaviorType.GAMBLING],
            gambling_consumption
        )
        
        # Deplete self-control
        agent.internal_state.self_control_resource -= 0.15
        agent.internal_state.self_control_resource = max(0, agent.internal_state.self_control_resource)
        
        # Increase stress if lost money
        if outcome.monetary_change < 0:
            stress_increase = min(0.2, abs(outcome.monetary_change) / agent.internal_state.wealth)
            agent.internal_state.stress += stress_increase
            agent.internal_state.stress = min(1, agent.internal_state.stress)
        
        # Update gambling tracking
        gambling_context = agent.gambling_context
        gambling_context.total_games += 1
        
        if outcome.monetary_change > 0:
            gambling_context.total_wins += outcome.monetary_change
        else:
            gambling_context.total_losses += abs(outcome.monetary_change)
    
    def _apply_drinking_outcome(self, agent: 'Agent', outcome: DrinkingOutcome) -> None:
        """Apply drinking outcome to agent state."""
        if not outcome.success:
            return
            
        # Update wealth
        agent.internal_state.wealth -= outcome.cost
        agent.internal_state.wealth = max(0, agent.internal_state.wealth)
        
        # Update mood and stress
        agent.internal_state.mood += outcome.mood_change
        agent.internal_state.stress -= outcome.stress_relief
        agent.internal_state.mood = np.clip(agent.internal_state.mood, -1, 1)
        agent.internal_state.stress = np.clip(agent.internal_state.stress, 0, 1)
        
        # Update addiction and habit
        alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
        
        # Reset withdrawal
        alcohol_state.time_since_last_use = 0
        alcohol_state.withdrawal_severity = 0.0
        
        # Update addiction stock
        consumption = outcome.units_consumed / 10.0  # Normalize units
        alcohol_state.stock = agent.addiction_module.update_addiction_stock(
            alcohol_state.stock,
            consumption
        )
        
        # Update tolerance
        tolerance_increase = consumption * 0.02  # Slow tolerance build
        alcohol_state.tolerance_level += tolerance_increase
        alcohol_state.tolerance_level = min(1.0, alcohol_state.tolerance_level)
        
        # Update habit stock
        agent.habit_stocks[BehaviorType.DRINKING] = agent.habit_formation.update_habit_stock(
            agent.habit_stocks[BehaviorType.DRINKING],
            consumption
        )
        
        # Deplete self-control
        agent.internal_state.self_control_resource -= 0.1 * consumption
        agent.internal_state.self_control_resource = max(0, agent.internal_state.self_control_resource)
    
    def _apply_begging_outcome(self, agent: 'Agent', outcome: BeggingOutcome) -> None:
        """Apply begging outcome to agent state."""
        if not outcome.success:
            return
            
        # Update wealth
        agent.internal_state.wealth += outcome.income
        
        # Apply social cost (reduced mood and increased stress)
        agent.internal_state.mood -= outcome.social_cost
        agent.internal_state.stress += outcome.social_cost * 0.5
        
        agent.internal_state.mood = np.clip(agent.internal_state.mood, -1, 1)
        agent.internal_state.stress = np.clip(agent.internal_state.stress, 0, 1)
    
    def _apply_job_search_outcome(self, agent: 'Agent', outcome: JobSearchOutcome) -> None:
        """Apply job search outcome to agent state."""
        if not outcome.success:
            return
            
        # Update stress
        agent.internal_state.stress += outcome.stress_change
        agent.internal_state.stress = np.clip(agent.internal_state.stress, 0, 1)
        
        if outcome.job_found:
            # Create new employment info
            base_salary = 1500.0 + outcome.job_quality * 2000.0  # $1500-3500 based on quality
            agent.employment = EmploymentInfo(
                job_quality=outcome.job_quality,
                base_salary=base_salary
            )
            
            # Update monthly expenses (higher salary jobs may have higher expenses)
            agent.internal_state.monthly_expenses = 600.0 + outcome.job_quality * 400.0
            
            # Improve mood from finding job
            agent.internal_state.mood += 0.3
            agent.internal_state.mood = min(1, agent.internal_state.mood)
    
    def _apply_housing_search_outcome(self, agent: 'Agent', outcome: HousingSearchOutcome) -> None:
        """Apply housing search outcome to agent state."""
        if not outcome.success:
            return
            
        if outcome.housing_found:
            # Create new housing info
            agent.home = HousingInfo(
                housing_quality=outcome.housing_quality,
                monthly_rent=outcome.rent_cost
            )
            
            # Update mood and reduce stress from finding housing
            agent.internal_state.mood += 0.2
            agent.internal_state.stress -= 0.1
            
            agent.internal_state.mood = min(1, agent.internal_state.mood)
            agent.internal_state.stress = max(0, agent.internal_state.stress)
    
    def _apply_move_outcome(self, agent: 'Agent', outcome: MoveOutcome) -> None:
        """Apply moving outcome to agent state."""
        if not outcome.success:
            return
            
        # Update wealth
        agent.internal_state.wealth -= outcome.move_cost
        agent.internal_state.wealth = max(0, agent.internal_state.wealth)
        
        # Update stress
        agent.internal_state.stress += outcome.stress_change
        agent.internal_state.stress = min(1, agent.internal_state.stress)
    
    def _apply_rest_outcome(self, agent: 'Agent', outcome: RestOutcome) -> None:
        """Apply rest outcome to agent state."""
        if not outcome.success:
            return
            
        # Apply all recovery effects
        agent.internal_state.stress -= outcome.stress_reduction
        agent.internal_state.mood += outcome.mood_improvement
        agent.internal_state.self_control_resource += outcome.self_control_restoration
        
        # Ensure bounds
        agent.internal_state.stress = max(0, agent.internal_state.stress)
        agent.internal_state.mood = np.clip(agent.internal_state.mood, -1, 1)
        agent.internal_state.self_control_resource = min(1, agent.internal_state.self_control_resource) 