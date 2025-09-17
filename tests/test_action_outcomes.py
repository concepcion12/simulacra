"""
Tests for Phase 4.1: Action Outcomes System

Tests comprehensive outcome generation, stochastic elements, 
and state update pipeline for all action types.
"""
import pytest
import numpy as np
from typing import List

from simulacra.agents.agent import Agent
from simulacra.agents.decision_making import Action
from simulacra.agents.action_outcomes import ActionOutcomeGenerator, StateUpdater, OutcomeContext
from simulacra.utils.types import (
    ActionType,
    ActionOutcome,
    WorkOutcome,
    GamblingOutcome,
    DrinkingOutcome,
    BeggingOutcome,
    JobSearchOutcome,
    HousingSearchOutcome,
    MoveOutcome,
    RestOutcome,
    BehaviorType,
    EmploymentInfo,
    SubstanceType,
)


class TestActionOutcomeGeneration:
    """Test outcome generation for different action types."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = Agent.create_with_profile('balanced', initial_wealth=1000.0)
        self.agent.employment = EmploymentInfo(job_quality=0.7, base_salary=2000.0)
        self.outcome_generator = ActionOutcomeGenerator(random_seed=42)
        self.context = OutcomeContext(
            district_wealth=0.6,
            location_quality=0.7,
            market_conditions=0.5,
            social_density=0.8
        )
    
    def test_work_outcome_generation(self):
        """Test work outcome generation and state dependency."""
        action = Action(ActionType.WORK, 40.0)  # Part-time work
        
        # Test normal work
        outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        assert isinstance(outcome, WorkOutcome)
        assert outcome.success
        assert outcome.payment > 0
        assert 0.1 <= outcome.performance <= 1.5
        assert outcome.stress_increase >= 0
        
        # Test work under stress
        self.agent.internal_state.stress = 0.8
        stressed_outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        # Performance should be lower when stressed
        assert stressed_outcome.performance < outcome.performance
        assert stressed_outcome.stress_increase > outcome.stress_increase
    
    def test_gambling_outcome_stochastic(self):
        """Test gambling outcomes with stochastic elements and biases."""
        action = Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 50.0})
        
        # Run multiple gambling sessions to test stochastic elements
        outcomes = []
        for _ in range(20):
            outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
            outcomes.append(outcome)
        
        # Should have mix of wins and losses
        wins = [o for o in outcomes if o.monetary_change > 0]
        losses = [o for o in outcomes if o.monetary_change < 0]
        near_misses = [o for o in outcomes if o.was_near_miss]
        
        assert len(wins) > 0, "Should have some wins"
        assert len(losses) > 0, "Should have some losses"
        assert len(near_misses) > 0, "Should have some near misses"
        
        # Test gambler's fallacy bias
        self.agent.gambling_context.loss_streak = 5
        biased_action = Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 50.0})
        biased_outcome = self.outcome_generator.generate_outcome(self.agent, biased_action, self.context)
        
        # Loss streak should increase bet amount (but this is internal to outcome generation)
        assert isinstance(biased_outcome, GamblingOutcome)
    
    def test_drinking_outcome_tolerance(self):
        """Test drinking outcomes with tolerance and addiction effects."""
        action = Action(ActionType.DRINK, 2.0, parameters={'units': 3})
        
        # Test drinking with low tolerance
        outcome1 = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        assert isinstance(outcome1, DrinkingOutcome)
        assert outcome1.success
        assert outcome1.cost > 0
        assert outcome1.units_consumed > 0
        assert outcome1.stress_relief > 0
        
        # Simulate tolerance buildup
        self.agent.addiction_states[SubstanceType.ALCOHOL].tolerance_level = 0.8
        
        # Test drinking with high tolerance
        outcome2 = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        # Effects should be reduced with tolerance
        assert outcome2.stress_relief < outcome1.stress_relief
    
    def test_begging_outcome_variability(self):
        """Test begging outcomes with high income variability."""
        action = Action(ActionType.BEG, 8.0)
        
        # Run multiple begging sessions
        incomes = []
        for _ in range(50):
            outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
            incomes.append(outcome.income)
        
        # Should have high variability (exponential distribution)
        income_std = np.std(incomes)
        income_mean = np.mean(incomes)
        
        assert income_std > 0, "Should have income variability"
        assert income_mean > 0, "Should have positive average income"
        
        # Test district wealth effect
        poor_context = OutcomeContext(district_wealth=0.2, location_quality=0.5, social_density=0.8)
        poor_outcome = self.outcome_generator.generate_outcome(self.agent, action, poor_context)
        
        rich_context = OutcomeContext(district_wealth=0.9, location_quality=0.5, social_density=0.8)
        rich_outcome = self.outcome_generator.generate_outcome(self.agent, action, rich_context)
        
        # Should generally earn more in richer districts (but with variance)
        # Test over multiple runs to account for stochasticity
        poor_incomes = [self.outcome_generator.generate_outcome(self.agent, action, poor_context).income 
                       for _ in range(20)]
        rich_incomes = [self.outcome_generator.generate_outcome(self.agent, action, rich_context).income 
                       for _ in range(20)]
        
        assert np.mean(rich_incomes) > np.mean(poor_incomes)
    
    def test_job_search_outcome_state_dependency(self):
        """Test job search outcomes depend on agent state."""
        self.agent.employment = None  # Make agent unemployed
        action = Action(ActionType.FIND_JOB, 20.0)
        
        # Test job search with good mood
        self.agent.internal_state.mood = 0.5
        self.agent.internal_state.stress = 0.2
        good_outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        # Test job search with poor state
        self.agent.internal_state.mood = -0.5
        self.agent.internal_state.stress = 0.8
        poor_outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        # Run multiple times to test probabilities
        good_successes = 0
        poor_successes = 0
        
        for _ in range(20):
            self.agent.internal_state.mood = 0.5
            self.agent.internal_state.stress = 0.2
            if self.outcome_generator.generate_outcome(self.agent, action, self.context).job_found:
                good_successes += 1
                
            self.agent.internal_state.mood = -0.5
            self.agent.internal_state.stress = 0.8
            if self.outcome_generator.generate_outcome(self.agent, action, self.context).job_found:
                poor_successes += 1
        
        # Good state should have higher success rate
        assert good_successes >= poor_successes
    
    def test_rest_outcome_recovery(self):
        """Test rest outcomes provide appropriate recovery."""
        self.agent.internal_state.stress = 0.8
        self.agent.internal_state.mood = -0.3
        self.agent.internal_state.self_control_resource = 0.4
        
        action = Action(ActionType.REST, 4.0)
        outcome = self.outcome_generator.generate_outcome(self.agent, action, self.context)
        
        assert isinstance(outcome, RestOutcome)
        assert outcome.success
        assert outcome.stress_reduction > 0
        assert outcome.self_control_restoration > 0
        # Mood improvement can be positive or negative due to randomness
    
    def test_action_failure_handling(self):
        """Test action failures and constraint handling."""
        # Test work without employment
        self.agent.employment = None
        work_action = Action(ActionType.WORK, 40.0)
        work_outcome = self.outcome_generator.generate_outcome(self.agent, work_action, self.context)
        
        assert not work_outcome.success
        assert work_outcome.payment == 0.0
        
        # Test gambling without money
        self.agent.internal_state.wealth = 0.0
        gamble_action = Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 50.0})
        gamble_outcome = self.outcome_generator.generate_outcome(self.agent, gamble_action, self.context)
        
        assert not gamble_outcome.success
        assert gamble_outcome.monetary_change == 0.0
        
        # Test drinking without money
        drink_action = Action(ActionType.DRINK, 2.0, parameters={'units': 3})
        drink_outcome = self.outcome_generator.generate_outcome(self.agent, drink_action, self.context)
        
        assert not drink_outcome.success
        assert drink_outcome.cost == 0.0


class TestStateUpdater:
    """Test state update pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = Agent.create_with_profile('balanced', initial_wealth=1000.0)
        self.state_updater = StateUpdater()
    
    def test_work_outcome_state_update(self):
        """Test work outcome updates agent state correctly."""
        initial_wealth = self.agent.internal_state.wealth
        initial_stress = self.agent.internal_state.stress
        initial_self_control = self.agent.internal_state.self_control_resource
        
        outcome = WorkOutcome(
            success=True,
            payment=500.0,
            performance=0.9,
            stress_increase=0.1
        )
        
        self.state_updater.apply_outcome(self.agent, outcome)
        
        # Check state updates
        assert self.agent.internal_state.wealth == initial_wealth + 500.0
        assert self.agent.internal_state.stress == initial_stress + 0.1
        assert self.agent.internal_state.self_control_resource < initial_self_control
    
    def test_gambling_outcome_state_update(self):
        """Test gambling outcome updates habits and gambling context."""
        initial_gambling_habit = self.agent.habit_stocks[BehaviorType.GAMBLING]
        initial_wealth = self.agent.internal_state.wealth
        
        outcome = GamblingOutcome(
            success=True,
            monetary_change=-50.0,
            was_near_miss=False,
            psychological_impact=-0.2
        )
        
        self.state_updater.apply_outcome(self.agent, outcome)
        
        # Check state updates
        assert self.agent.internal_state.wealth == initial_wealth - 50.0
        assert self.agent.habit_stocks[BehaviorType.GAMBLING] > initial_gambling_habit
        assert self.agent.internal_state.mood < 0  # Should be negative from loss
    
    def test_drinking_outcome_addiction_update(self):
        """Test drinking outcome updates addiction state correctly."""
        initial_addiction = self.agent.addiction_states[SubstanceType.ALCOHOL].stock
        initial_habit = self.agent.habit_stocks[BehaviorType.DRINKING]
        
        outcome = DrinkingOutcome(
            success=True,
            cost=30.0,
            units_consumed=3,
            stress_relief=0.3,
            mood_change=0.2
        )
        
        self.state_updater.apply_outcome(self.agent, outcome)
        
        # Check addiction updates
        alcohol_state = self.agent.addiction_states[SubstanceType.ALCOHOL]
        assert alcohol_state.stock > initial_addiction
        assert alcohol_state.time_since_last_use == 0  # Reset withdrawal timer
        assert alcohol_state.tolerance_level > 0  # Should increase tolerance
        assert self.agent.habit_stocks[BehaviorType.DRINKING] > initial_habit
    
    def test_rest_outcome_recovery_update(self):
        """Test rest outcome provides state recovery."""
        # Set agent in poor state
        self.agent.internal_state.stress = 0.8
        self.agent.internal_state.mood = -0.4
        self.agent.internal_state.self_control_resource = 0.3
        
        outcome = RestOutcome(
            success=True,
            stress_reduction=0.3,
            mood_improvement=0.2,
            self_control_restoration=0.4
        )
        
        self.state_updater.apply_outcome(self.agent, outcome)
        
        # Check recovery
        assert self.agent.internal_state.stress == 0.5  # 0.8 - 0.3
        assert self.agent.internal_state.mood == -0.2  # -0.4 + 0.2
        assert self.agent.internal_state.self_control_resource == 0.7  # 0.3 + 0.4


class TestIntegratedActionExecution:
    """Test complete action execution pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = Agent.create_with_profile('vulnerable', initial_wealth=500.0)
        self.agent.employment = EmploymentInfo(job_quality=0.6, base_salary=1500.0)
        self.context = OutcomeContext(
            district_wealth=0.4,
            location_quality=0.6,
            market_conditions=0.7,
            social_density=0.5
        )
    
    def test_complete_action_execution(self):
        """Test complete action execution with outcome generation and state update."""
        initial_wealth = self.agent.internal_state.wealth
        initial_time_budget = self.agent.action_budget.remaining_hours
        
        # Execute work action
        work_action = Action(ActionType.WORK, 20.0)
        outcome = self.agent.execute_action(work_action, self.context)
        
        # Check outcome generated
        assert isinstance(outcome, WorkOutcome)
        assert outcome.success
        
        # Check state updated
        assert self.agent.internal_state.wealth > initial_wealth
        assert self.agent.action_budget.remaining_hours == initial_time_budget - 20.0
        
        # Check action recorded
        assert len(self.agent.action_history) == 1
        assert self.agent.action_history[0][0] == work_action
        assert self.agent.action_history[0][1] == outcome
    
    def test_addiction_progression_simulation(self):
        """Test addiction progression through repeated drinking."""
        # Start with low addiction
        initial_addiction = self.agent.addiction_states[SubstanceType.ALCOHOL].stock
        assert initial_addiction == 0.0
        
        # Simulate repeated drinking over time
        for day in range(10):
            drink_action = Action(ActionType.DRINK, 2.0, parameters={'units': 2})
            self.agent.execute_action(drink_action, self.context)
            
            # Progress time to allow addiction buildup
            if day % 3 == 0:
                self.agent.update_internal_states(delta_time=1)
        
        # Check addiction progression
        final_addiction = self.agent.addiction_states[SubstanceType.ALCOHOL].stock
        assert final_addiction > initial_addiction
        
        # Check habit formation
        final_habit = self.agent.habit_stocks[BehaviorType.DRINKING]
        assert final_habit > 0
    
    def test_financial_stress_gambling_spiral(self):
        """Test financial pressure leading to gambling behavior."""
        # Set agent in financial distress
        self.agent.internal_state.wealth = 200.0  # Below monthly expenses
        self.agent.internal_state.stress = 0.8
        
        initial_wealth = self.agent.internal_state.wealth
        
        # Simulate gambling attempts
        gambling_losses = 0
        for _ in range(5):
            if self.agent.internal_state.wealth > 50:  # Can afford to gamble
                gamble_action = Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 50.0})
                outcome = self.agent.execute_action(gamble_action, self.context)
                
                if outcome.monetary_change < 0:
                    gambling_losses += 1
        
        # Financial situation should generally worsen (house edge)
        assert self.agent.internal_state.wealth <= initial_wealth
        assert gambling_losses > 0  # Should have some losses
    
    def test_multiple_outcome_types(self):
        """Test different outcome types in sequence."""
        outcomes = []
        
        # Work to earn money
        work_action = Action(ActionType.WORK, 40.0)
        work_outcome = self.agent.execute_action(work_action, self.context)
        outcomes.append(work_outcome)
        
        # Drink to relieve stress
        drink_action = Action(ActionType.DRINK, 2.0, parameters={'units': 2})
        drink_outcome = self.agent.execute_action(drink_action, self.context)
        outcomes.append(drink_outcome)
        
        # Rest to recover
        rest_action = Action(ActionType.REST, 4.0)
        rest_outcome = self.agent.execute_action(rest_action, self.context)
        outcomes.append(rest_outcome)
        
        # Check all outcomes generated correctly
        assert isinstance(outcomes[0], WorkOutcome)
        assert isinstance(outcomes[1], DrinkingOutcome)
        assert isinstance(outcomes[2], RestOutcome)
        # Check all were successful
        assert all(outcome.success for outcome in outcomes)
        
        # Check action history
        assert len(self.agent.action_history) == 3


if __name__ == "__main__":
    # Run a simple demonstration
    print("=== Phase 4.1 Action Outcomes System Demo ===\n")
    
    # Create agent
    agent = Agent.create_with_profile('vulnerable', initial_wealth=800.0)
    agent.employment = "Construction Worker"
    
    # Create context
    context = OutcomeContext(
        district_wealth=0.3,  # Poor district
        location_quality=0.4,
        market_conditions=0.6,
        social_density=0.7
    )
    
    print(f"Agent: {agent.name}")
    print(f"Initial State: Wealth=${agent.internal_state.wealth:.2f}, "
          f"Stress={agent.internal_state.stress:.2f}, "
          f"Mood={agent.internal_state.mood:.2f}")
    print()
    
    # Simulate a day of activities
    actions = [
        Action(ActionType.WORK, 8.0),
        Action(ActionType.DRINK, 2.0, parameters={'units': 3}),
        Action(ActionType.GAMBLE, 3.0, parameters={'bet_amount': 30.0}),
        Action(ActionType.REST, 4.0),
        Action(ActionType.SOCIALIZE, 2.0)
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"Action {i}: {action.action_type.name}")
        outcome = agent.execute_action(action, context)
        
        print(f"  Outcome: {outcome.message}")
        print(f"  Success: {outcome.success}")
        
        if hasattr(outcome, 'payment') and outcome.payment:
            print(f"  Payment: ${outcome.payment:.2f}")
        if hasattr(outcome, 'monetary_change') and outcome.monetary_change:
            print(f"  Money change: ${outcome.monetary_change:.2f}")
        if hasattr(outcome, 'cost') and outcome.cost:
            print(f"  Cost: ${outcome.cost:.2f}")
        
        print(f"  New State: Wealth=${agent.internal_state.wealth:.2f}, "
              f"Stress={agent.internal_state.stress:.2f}, "
              f"Mood={agent.internal_state.mood:.2f}")
        print()
    
    print(f"Final time budget remaining: {agent.action_budget.remaining_hours:.1f}h")
    print(f"Actions in history: {len(agent.action_history)}")
    
    # Show addiction progression
    alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
    print(f"\nAddiction state:")
    print(f"  Stock: {alcohol_state.stock:.3f}")
    print(f"  Tolerance: {alcohol_state.tolerance_level:.3f}")
    print(f"  Habit (drinking): {agent.habit_stocks[BehaviorType.DRINKING]:.3f}")
    print(f"  Habit (gambling): {agent.habit_stocks[BehaviorType.GAMBLING]:.3f}") 
