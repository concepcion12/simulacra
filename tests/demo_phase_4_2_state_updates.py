"""
Demo for Phase 4.2: State Updates from Actions

Demonstrates comprehensive state tracking:
- Work performance history
- Gambling win/loss tracking  
- Social network updates
- Job and housing assignment
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from src.agents.agent import Agent
from src.agents.decision_making import Action
from src.agents.action_outcomes import OutcomeContext
from src.utils.types import ActionType


def demo_work_performance_tracking():
    """Demonstrate work performance tracking over multiple months."""
    print("=== Work Performance Tracking Demo ===\n")
    
    # Create employed agent
    agent = Agent.create_with_profile('balanced', initial_wealth=1000.0)
    
    # Find a job first
    job_action = Action(ActionType.FIND_JOB, 20.0)
    context = OutcomeContext(market_conditions=0.8)
    
    # Keep trying until job found
    for attempt in range(10):
        outcome = agent.execute_action(job_action, context)
        if hasattr(outcome, 'job_found') and outcome.job_found:
            print(f"Found job! Quality: {outcome.job_quality:.2f}")
            print(f"Base salary: ${agent.employment.base_salary:.2f}")
            break
    
    if agent.employment is None:
        print("Failed to find job")
        return
    
    print("\nWorking for 6 months...")
    work_action = Action(ActionType.WORK, 40.0)  # Part-time work
    
    for month in range(6):
        # Vary agent state to show performance impact
        if month == 3:
            agent.internal_state.stress = 0.8
            print(f"\nMonth {month+1}: High stress period")
        else:
            agent.internal_state.stress = 0.3
            
        outcome = agent.execute_action(work_action, context)
        
        print(f"Month {month+1}: Performance = {outcome.performance:.2f}, "
              f"Payment = ${outcome.payment:.2f}")
    
    # Show performance history
    perf_history = agent.employment.performance_history
    print(f"\nPerformance Summary:")
    print(f"- Average performance: {perf_history.average_performance:.2f}")
    print(f"- Months employed: {perf_history.months_employed}")
    print(f"- Warnings received: {perf_history.warnings_received}")
    print(f"- Recent performances: {[f'{p:.2f}' for p in perf_history.recent_performances]}")


def demo_gambling_tracking():
    """Demonstrate gambling win/loss tracking."""
    print("\n\n=== Gambling Win/Loss Tracking Demo ===\n")
    
    agent = Agent.create_with_profile('impulsive', initial_wealth=500.0)
    gamble_action = Action(ActionType.GAMBLE, 2.0, parameters={'bet_amount': 20.0})
    context = OutcomeContext()
    
    print("Gambling 10 times...")
    wins = 0
    losses = 0
    
    for i in range(10):
        initial_wealth = agent.internal_state.wealth
        outcome = agent.execute_action(gamble_action, context)
        
        if outcome.monetary_change > 0:
            wins += 1
            result = f"Won ${outcome.monetary_change:.2f}"
        else:
            losses += 1
            result = f"Lost ${abs(outcome.monetary_change):.2f}"
            
        print(f"Game {i+1}: {result} (Wealth: ${agent.internal_state.wealth:.2f})")
    
    # Show gambling statistics
    gambling_context = agent.gambling_context
    print(f"\nGambling Statistics:")
    print(f"- Total games: {gambling_context.total_games}")
    print(f"- Total wins: ${gambling_context.total_wins:.2f}")
    print(f"- Total losses: ${gambling_context.total_losses:.2f}")
    print(f"- Net result: ${gambling_context.total_wins - gambling_context.total_losses:.2f}")
    print(f"- Current loss streak: {gambling_context.loss_streak}")
    print(f"- Win rate: {wins/10:.1%}")


def demo_social_network_building():
    """Demonstrate social network updates."""
    print("\n\n=== Social Network Building Demo ===\n")
    
    agent = Agent.create_with_profile('balanced', initial_wealth=800.0)
    socialize_action = Action(ActionType.SOCIALIZE, 3.0)
    
    print(f"Initial social connections: {len(agent.social_connections)}")
    
    # Socialize multiple times with varying conditions
    for i in range(5):
        # Vary social context
        if i < 2:
            context = OutcomeContext(social_density=0.9)  # High density, more likely to meet people
            agent.internal_state.mood = 0.5  # Good mood
            print(f"\nSocializing {i+1}: High density area, good mood")
        else:
            context = OutcomeContext(social_density=0.3)  # Low density
            agent.internal_state.mood = -0.3  # Poor mood
            print(f"\nSocializing {i+1}: Low density area, poor mood")
            
        outcome = agent.execute_action(socialize_action, context)
        
        print(f"- New connections: {outcome.social_connections_gained}")
        print(f"- Mood change: {outcome.mood_change:+.2f}")
        print(f"- Social influence: {outcome.social_influence_received:.2f}")
        print(f"- Total connections: {len(agent.social_connections)}")
        
        # Check if social influence affected habits
        if outcome.social_influence_received > 0.5:
            print(f"  * High social influence may affect behaviors!")
            print(f"  * Gambling habit: {agent.habit_stocks[BehaviorType.GAMBLING]:.3f}")


def demo_housing_search():
    """Demonstrate housing search and assignment."""
    print("\n\n=== Housing Search Demo ===\n")
    
    agent = Agent.create_with_profile('balanced', initial_wealth=2000.0)
    housing_action = Action(ActionType.FIND_HOUSING, 10.0)
    
    print(f"Initial housing: {agent.home}")
    print(f"Initial wealth: ${agent.internal_state.wealth:.2f}")
    
    # Try to find housing
    context = OutcomeContext(market_conditions=0.7)
    
    for attempt in range(5):
        print(f"\nHousing search attempt {attempt+1}:")
        outcome = agent.execute_action(housing_action, context)
        
        if hasattr(outcome, 'housing_found') and outcome.housing_found:
            print(f"Found housing!")
            print(f"- Quality: {outcome.housing_quality:.2f}")
            print(f"- Rent: ${outcome.rent_cost:.2f}/month")
            print(f"- Agent mood: {agent.internal_state.mood:.2f}")
            print(f"- Agent stress: {agent.internal_state.stress:.2f}")
            break
        else:
            print("No suitable housing found")
            # Stress increases with failed searches
            print(f"- Agent stress: {agent.internal_state.stress:.2f}")
    
    if agent.home:
        print(f"\nFinal housing info:")
        print(f"- Quality: {agent.home.housing_quality:.2f}")
        print(f"- Monthly rent: ${agent.home.monthly_rent:.2f}")


def demo_integrated_state_updates():
    """Demonstrate how all state updates work together."""
    print("\n\n=== Integrated State Updates Demo ===\n")
    
    # Create unemployed, homeless agent
    agent = Agent.create_with_profile('vulnerable', initial_wealth=500.0)
    
    print("Starting state:")
    print(f"- Wealth: ${agent.internal_state.wealth:.2f}")
    print(f"- Employment: {agent.employment}")
    print(f"- Housing: {agent.home}")
    print(f"- Stress: {agent.internal_state.stress:.2f}")
    print(f"- Mood: {agent.internal_state.mood:.2f}")
    
    context = OutcomeContext(
        market_conditions=0.6,
        social_density=0.7,
        district_wealth=0.5
    )
    
    # Day 1: Try to find job
    print("\n--- Day 1: Job Search ---")
    job_action = Action(ActionType.FIND_JOB, 8.0)
    outcome = agent.execute_action(job_action, context)
    print(f"Job found: {getattr(outcome, 'job_found', False)}")
    
    # Day 2: Try begging for money
    print("\n--- Day 2: Begging ---")
    beg_action = Action(ActionType.BEG, 6.0)
    outcome = agent.execute_action(beg_action, context)
    print(f"Income: ${outcome.income:.2f}")
    print(f"Social cost impact on mood: {outcome.social_cost:.2f}")
    
    # Day 3: Socialize to improve mood
    print("\n--- Day 3: Socializing ---")
    socialize_action = Action(ActionType.SOCIALIZE, 4.0)
    outcome = agent.execute_action(socialize_action, context)
    print(f"Mood change: {outcome.mood_change:+.2f}")
    print(f"New connections: {outcome.social_connections_gained}")
    
    # Day 4: Gambling out of desperation
    print("\n--- Day 4: Gambling ---")
    gamble_action = Action(ActionType.GAMBLE, 3.0, parameters={'bet_amount': 30.0})
    outcome = agent.execute_action(gamble_action, context)
    print(f"Result: ${outcome.monetary_change:+.2f}")
    print(f"Psychological impact: {outcome.psychological_impact:+.2f}")
    
    # Day 5: Drinking to cope
    print("\n--- Day 5: Drinking ---")
    # First need housing to drink at home
    if agent.home is None:
        print("Can't drink at home without housing, trying to find housing first...")
        housing_action = Action(ActionType.FIND_HOUSING, 4.0)
        housing_outcome = agent.execute_action(housing_action, context)
        if hasattr(housing_outcome, 'housing_found') and housing_outcome.housing_found:
            print("Found housing!")
    
    if agent.home:
        drink_action = Action(ActionType.DRINK, 2.0, parameters={'units': 4})
        outcome = agent.execute_action(drink_action, context)
        print(f"Units consumed: {outcome.units_consumed}")
        print(f"Stress relief: {outcome.stress_relief:.2f}")
        print(f"Mood change: {outcome.mood_change:+.2f}")
    
    print("\n--- Final State ---")
    print(f"- Wealth: ${agent.internal_state.wealth:.2f}")
    print(f"- Employment: {'Yes' if agent.employment else 'No'}")
    print(f"- Housing: {'Yes' if agent.home else 'No'}")
    print(f"- Stress: {agent.internal_state.stress:.2f}")
    print(f"- Mood: {agent.internal_state.mood:.2f}")
    print(f"- Social connections: {len(agent.social_connections)}")
    print(f"- Gambling habit: {agent.habit_stocks[BehaviorType.GAMBLING]:.3f}")
    print(f"- Drinking habit: {agent.habit_stocks[BehaviorType.DRINKING]:.3f}")
    print(f"- Alcohol addiction: {agent.addiction_states[SubstanceType.ALCOHOL].stock:.3f}")


if __name__ == "__main__":
    # Run all demos
    from src.utils.types import BehaviorType, SubstanceType
    
    demo_work_performance_tracking()
    demo_gambling_tracking()
    demo_social_network_building()
    demo_housing_search()
    demo_integrated_state_updates() 
