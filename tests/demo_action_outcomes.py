"""
Standalone demo for Phase 4.1: Action Outcomes System

Demonstrates comprehensive outcome generation, stochastic elements, 
and state update pipeline for all action types.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from src.agents.agent import Agent
from src.agents.decision_making import Action
from src.agents.action_outcomes import ActionOutcomeGenerator, StateUpdater, OutcomeContext
from src.utils.types import (
    ActionType, ActionOutcome, WorkOutcome, GamblingOutcome, DrinkingOutcome,
    BeggingOutcome, JobSearchOutcome, HousingSearchOutcome, MoveOutcome,
    RestOutcome, SocializeOutcome, BehaviorType, SubstanceType
)


def demo_basic_outcomes():
    """Demonstrate basic outcome generation for different action types."""
    print("=== Basic Outcome Generation Demo ===\n")
    
    # Create agent and context
    agent = Agent.create_with_profile('balanced', initial_wealth=1000.0)
    agent.employment = "Office Worker"
    
    outcome_generator = ActionOutcomeGenerator(random_seed=42)
    context = OutcomeContext(
        district_wealth=0.6,
        location_quality=0.7,
        market_conditions=0.5,
        social_density=0.8
    )
    
    # Test different action types
    actions = [
        Action(ActionType.WORK, 40.0),
        Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 50.0}),
        Action(ActionType.DRINK, 2.0, parameters={'units': 3}),
        Action(ActionType.BEG, 8.0),
        Action(ActionType.REST, 4.0),
        Action(ActionType.SOCIALIZE, 3.0)
    ]
    
    for action in actions:
        print(f"Testing {action.action_type.name}:")
        outcome = outcome_generator.generate_outcome(agent, action, context)
        print(f"  Success: {outcome.success}")
        print(f"  Message: {outcome.message}")
        
        # Show specific outcome details
        if isinstance(outcome, WorkOutcome):
            print(f"  Payment: ${outcome.payment:.2f}")
            print(f"  Performance: {outcome.performance:.2f}")
        elif isinstance(outcome, GamblingOutcome):
            print(f"  Money change: ${outcome.monetary_change:.2f}")
            print(f"  Near miss: {outcome.was_near_miss}")
        elif isinstance(outcome, DrinkingOutcome):
            print(f"  Cost: ${outcome.cost:.2f}")
            print(f"  Units: {outcome.units_consumed}")
        elif isinstance(outcome, BeggingOutcome):
            print(f"  Income: ${outcome.income:.2f}")
            print(f"  Social cost: {outcome.social_cost:.2f}")
        
        print()


def demo_stochastic_elements():
    """Demonstrate stochastic elements in gambling and begging."""
    print("=== Stochastic Elements Demo ===\n")
    
    agent = Agent.create_with_profile('impulsive', initial_wealth=1000.0)
    outcome_generator = ActionOutcomeGenerator()
    context = OutcomeContext(district_wealth=0.5, location_quality=0.5, social_density=0.7)
    
    # Test gambling variability
    print("Gambling outcomes (10 sessions):")
    gambling_results = []
    for i in range(10):
        action = Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 25.0})
        outcome = outcome_generator.generate_outcome(agent, action, context)
        gambling_results.append(outcome.monetary_change)
        
        result_type = "WIN" if outcome.monetary_change > 0 else "LOSS"
        if outcome.was_near_miss:
            result_type += " (Near Miss)"
        
        print(f"  Session {i+1}: {result_type} ${outcome.monetary_change:.2f}")
    
    wins = sum(1 for x in gambling_results if x > 0)
    total_change = sum(gambling_results)
    print(f"  Summary: {wins}/10 wins, Total: ${total_change:.2f}\n")
    
    # Test begging variability
    print("Begging outcomes (10 sessions):")
    begging_results = []
    for i in range(10):
        action = Action(ActionType.BEG, 8.0)
        outcome = outcome_generator.generate_outcome(agent, action, context)
        begging_results.append(outcome.income)
        print(f"  Session {i+1}: ${outcome.income:.2f}")
    
    avg_income = np.mean(begging_results)
    std_income = np.std(begging_results)
    print(f"  Summary: Avg=${avg_income:.2f}, Std=${std_income:.2f}\n")


def demo_state_updates():
    """Demonstrate state update pipeline."""
    print("=== State Update Pipeline Demo ===\n")
    
    agent = Agent.create_with_profile('vulnerable', initial_wealth=500.0)
    agent.employment = "Construction Worker"
    
    print(f"Initial State:")
    print(f"  Wealth: ${agent.internal_state.wealth:.2f}")
    print(f"  Stress: {agent.internal_state.stress:.2f}")
    print(f"  Mood: {agent.internal_state.mood:.2f}")
    print(f"  Self-control: {agent.internal_state.self_control_resource:.2f}")
    print(f"  Addiction stock: {agent.addiction_states[SubstanceType.ALCOHOL].stock:.3f}")
    print(f"  Drinking habit: {agent.habit_stocks[BehaviorType.DRINKING]:.3f}")
    print()
    
    # Simulate drinking
    print("Drinking 3 units...")
    drink_outcome = DrinkingOutcome(
        success=True,
        cost=30.0,
        units_consumed=3,
        stress_relief=0.4,
        mood_change=0.3,
        message="Had 3 drinks"
    )
    
    agent.state_updater.apply_outcome(agent, drink_outcome)
    
    print(f"After drinking:")
    print(f"  Wealth: ${agent.internal_state.wealth:.2f}")
    print(f"  Stress: {agent.internal_state.stress:.2f}")
    print(f"  Mood: {agent.internal_state.mood:.2f}")
    print(f"  Self-control: {agent.internal_state.self_control_resource:.2f}")
    print(f"  Addiction stock: {agent.addiction_states[SubstanceType.ALCOHOL].stock:.3f}")
    print(f"  Drinking habit: {agent.habit_stocks[BehaviorType.DRINKING]:.3f}")
    print()


def demo_complete_execution():
    """Demonstrate complete action execution pipeline."""
    print("=== Complete Action Execution Demo ===\n")
    
    # Create agent
    agent = Agent.create_with_profile('vulnerable', initial_wealth=800.0)
    agent.employment = "Retail Worker"
    
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
    print(f"Time budget: {agent.action_budget.remaining_hours:.1f}h")
    print()
    
    # Simulate a sequence of actions
    actions = [
        Action(ActionType.WORK, 8.0),
        Action(ActionType.DRINK, 2.0, parameters={'units': 2}),
        Action(ActionType.GAMBLE, 3.0, parameters={'bet_amount': 40.0}),
        Action(ActionType.REST, 6.0),
        Action(ActionType.SOCIALIZE, 2.0)
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"Action {i}: {action.action_type.name}")
        
        # Check if agent can afford action
        if not agent.action_budget.can_afford(action.time_cost):
            print(f"  Cannot afford - insufficient time budget")
            continue
            
        outcome = agent.execute_action(action, context)
        
        print(f"  Outcome: {outcome.message}")
        print(f"  Success: {outcome.success}")
        
        # Show financial changes
        if hasattr(outcome, 'payment') and outcome.payment:
            print(f"  Payment: ${outcome.payment:.2f}")
        if hasattr(outcome, 'monetary_change') and outcome.monetary_change != 0:
            print(f"  Money change: ${outcome.monetary_change:.2f}")
        if hasattr(outcome, 'cost') and outcome.cost:
            print(f"  Cost: ${outcome.cost:.2f}")
        
        print(f"  New State: Wealth=${agent.internal_state.wealth:.2f}, "
              f"Stress={agent.internal_state.stress:.2f}, "
              f"Mood={agent.internal_state.mood:.2f}")
        print(f"  Time remaining: {agent.action_budget.remaining_hours:.1f}h")
        print()
    
    print(f"Final summary:")
    print(f"  Actions executed: {len(agent.action_history)}")
    print(f"  Time used: {agent.action_budget.spent_hours:.1f}h")
    
    # Show addiction progression
    alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
    print(f"  Addiction progression:")
    print(f"    Stock: {alcohol_state.stock:.3f}")
    print(f"    Tolerance: {alcohol_state.tolerance_level:.3f}")
    print(f"    Drinking habit: {agent.habit_stocks[BehaviorType.DRINKING]:.3f}")
    print(f"    Gambling habit: {agent.habit_stocks[BehaviorType.GAMBLING]:.3f}")


def demo_action_constraints():
    """Demonstrate action constraints and failure handling."""
    print("=== Action Constraints and Failures Demo ===\n")
    
    agent = Agent.create_with_profile('balanced', initial_wealth=50.0)  # Low money
    agent.employment = None  # Unemployed
    
    outcome_generator = ActionOutcomeGenerator()
    context = OutcomeContext()
    
    print(f"Agent state: Wealth=${agent.internal_state.wealth:.2f}, Employed={agent.employment is not None}")
    print()
    
    # Test constraints
    constraints_tests = [
        (Action(ActionType.WORK, 40.0), "Work without employment"),
        (Action(ActionType.GAMBLE, 4.0, parameters={'bet_amount': 100.0}), "Gamble more than available wealth"),
        (Action(ActionType.DRINK, 2.0, parameters={'units': 5}), "Drink more than affordable"),
    ]
    
    for action, description in constraints_tests:
        print(f"Testing: {description}")
        outcome = outcome_generator.generate_outcome(agent, action, context)
        print(f"  Success: {outcome.success}")
        print(f"  Message: {outcome.message}")
        print()


if __name__ == "__main__":
    print("Phase 4.1: Action Outcomes System")
    print("=" * 50)
    print()
    
    try:
        demo_basic_outcomes()
        demo_stochastic_elements()
        demo_state_updates()
        demo_complete_execution()
        demo_action_constraints()
        
        print("\n✅ Phase 4.1 Action Outcomes System successfully implemented!")
        print("\nKey achievements:")
        print("• Outcome generation for all action types")
        print("• Stochastic elements (gambling wins/losses, begging income)")
        print("• Complete outcome → state update pipeline")
        print("• Action failure handling and constraints")
        print("• Addiction and habit progression")
        print("• Realistic behavioral dynamics")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc() 