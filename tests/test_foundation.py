"""
Test script to verify the foundation of the simulation is working.
"""
import sys
sys.path.append('.')

from src.agents import Agent
from src.utils.types import (
    ActionType, BehaviorType, SubstanceType,
    AlcoholCue, GamblingCue, FinancialStressCue
)


def test_agent_creation():
    """Test creating agents with different profiles."""
    print("Testing agent creation...")
    
    # Create random agent
    agent1 = Agent.create_random()
    print(f"Random agent: {agent1}")
    print(f"  Personality: impulsivity={agent1.personality.baseline_impulsivity:.2f}, "
          f"cognitive_type={agent1.personality.cognitive_type:.2f}")
    
    # Create agents with specific profiles
    profiles = ['impulsive', 'cautious', 'balanced', 'vulnerable']
    for profile in profiles:
        agent = Agent.create_with_profile(profile, initial_wealth=1500)
        print(f"\n{profile.capitalize()} agent: {agent}")
        print(f"  Addiction vulnerability: {agent.personality.addiction_vulnerability:.2f}")
        print(f"  Gambling bias: {agent.personality.gambling_bias_strength:.2f}")


def test_state_updates():
    """Test internal state updates."""
    print("\n\nTesting state updates...")
    
    agent = Agent.create_with_profile('vulnerable', initial_wealth=500)
    print(f"Initial state: {agent}")
    
    # Simulate stress
    agent.internal_state.stress = 0.8
    agent.update_internal_states()
    
    print(f"After stress update: stress={agent.internal_state.stress:.2f}, "
          f"craving={agent.craving_intensities[SubstanceType.ALCOHOL]:.2f}")
    
    # Simulate addiction development
    agent.addiction_states[SubstanceType.ALCOHOL].stock = 0.5
    agent.addiction_states[SubstanceType.ALCOHOL].time_since_last_use = 3
    agent.update_internal_states()
    
    print(f"With addiction: withdrawal={agent.addiction_states[SubstanceType.ALCOHOL].withdrawal_severity:.2f}, "
          f"craving={agent.craving_intensities[SubstanceType.ALCOHOL]:.2f}")


def test_environmental_cues():
    """Test environmental cue processing."""
    print("\n\nTesting environmental cues...")
    
    agent = Agent.create_with_profile('vulnerable')
    
    # Give agent some addiction/habit history
    agent.addiction_states[SubstanceType.ALCOHOL].stock = 0.3
    agent.habit_stocks[BehaviorType.GAMBLING] = 0.4
    agent.update_internal_states()
    
    print(f"Before cues: alcohol_craving={agent.craving_intensities[SubstanceType.ALCOHOL]:.2f}, "
          f"gambling_craving={agent.craving_intensities[BehaviorType.GAMBLING]:.2f}")
    
    # Process cues
    cues = [
        AlcoholCue(intensity=0.7),
        GamblingCue(intensity=0.5),
        FinancialStressCue(intensity=0.8)
    ]
    
    agent.process_environmental_cues(cues)
    
    print(f"After cues: alcohol_craving={agent.craving_intensities[SubstanceType.ALCOHOL]:.2f}, "
          f"gambling_craving={agent.craving_intensities[BehaviorType.GAMBLING]:.2f}, "
          f"stress={agent.internal_state.stress:.2f}")


def test_behavioral_economics():
    """Test behavioral economics modules."""
    print("\n\nTesting behavioral economics...")
    
    agent = Agent.create_with_profile('impulsive')
    
    # Test prospect theory
    outcomes = [-100, -50, 0, 50, 100]
    reference_point = agent.internal_state.wealth
    
    print("Prospect theory values (reference=wealth):")
    for outcome in outcomes:
        value = agent.prospect_theory.evaluate_outcome(
            reference_point + outcome,
            reference_point,
            agent.personality
        )
        print(f"  Outcome {outcome:+4d}: value={value:+.2f}")
    
    # Test temporal discounting
    future_utility = 100
    delays = [0, 1, 3, 6, 12]
    
    print("\nTemporal discounting (utility=100):")
    for delay in delays:
        discounted = agent.temporal_discounting.discount_future_utility(
            future_utility,
            delay,
            agent.personality,
            cognitive_load=0.5,
            craving_intensity=0.3
        )
        print(f"  Delay {delay:2d} months: discounted={discounted:.2f}")
    
    # Test dual process
    agent.internal_state.self_control_resource = 0.7
    agent.internal_state.stress = 0.6
    max_craving = 0.4
    
    theta = agent.dual_process.calculate_effective_theta(
        agent.personality,
        agent.internal_state.self_control_resource,
        agent.internal_state.cognitive_load,
        max_craving,
        agent.internal_state.stress
    )
    
    print(f"\nDual process theta: {theta:.2f} (base={agent.personality.cognitive_type:.2f})")


def test_action_budget():
    """Test action budget management."""
    print("\n\nTesting action budget...")
    
    agent = Agent()
    print(f"Initial budget: {agent.action_budget.remaining_hours} hours")
    
    # Simulate spending time
    actions = [
        ("Work", 160),
        ("Gambling", 4),
        ("Drinking", 2),
        ("Rest", 4)
    ]
    
    for action_name, hours in actions:
        if agent.action_budget.can_afford(hours):
            agent.action_budget.spend(hours)
            print(f"  {action_name}: spent {hours}h, remaining {agent.action_budget.remaining_hours}h")
        else:
            print(f"  {action_name}: CANNOT AFFORD {hours}h")
    
    # Reset for new month
    agent.action_budget.reset()
    print(f"After reset: {agent.action_budget.remaining_hours} hours")


if __name__ == "__main__":
    print("=== Simulacra Foundation Test ===\n")
    
    test_agent_creation()
    test_state_updates()
    test_environmental_cues()
    test_behavioral_economics()
    test_action_budget()
    
    print("\n=== All tests completed successfully! ===")
    print("\nThe foundation is ready. Next steps:")
    print("1. Implement the decision-making system (utility calculation, action selection)")
    print("2. Create the environment (City, Districts, Buildings)")
    print("3. Build the action execution system")
    print("4. Develop the main simulation loop")
    print("5. Add visualization and analysis tools") 