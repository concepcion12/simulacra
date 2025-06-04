"""
Environmental Cue System Demonstration

This script demonstrates the environmental cue system with various scenarios
showing how spatial, temporal, and social cues affect agents based on their
internal states and proximity to cue sources.
"""
import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import the ``src`` package
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.environment.cues import CueGenerator
from src.utils.types import (
    CueType, PlotID, Coordinate, SimulationTime,
    PersonalityTraits, InternalState, AddictionState,
    SubstanceType, BehaviorType
)
from src.agents.agent import Agent


def demonstrate_distance_based_intensity():
    """Demonstrate how cue intensity decreases with distance."""
    print("=== Distance-Based Cue Intensity ===")
    
    cue_generator = CueGenerator()
    base_intensity = 0.8
    max_radius = 3.0
    
    print(f"Base intensity: {base_intensity}")
    print(f"Max radius: {max_radius}")
    print("\nDistance → Intensity:")
    
    for distance in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        intensity = cue_generator.calculate_cue_intensity(
            distance=distance,
            base_intensity=base_intensity,
            max_radius=max_radius
        )
        print(f"  {distance:3.1f}m → {intensity:6.4f}")
    
    print()


def demonstrate_agent_state_modulation():
    """Demonstrate how agent state modulates cue reception."""
    print("=== Agent State Modulation ===")
    
    cue_generator = CueGenerator()
    
    # Create agents with different states
    agents = {
        "Healthy Agent": Agent.create_with_profile('cautious'),
        "Addicted Agent": Agent.create_with_profile('vulnerable'),
        "Stressed Agent": Agent.create_with_profile('balanced')
    }
    
    # Modify agent states
    agents["Addicted Agent"].addiction_states[SubstanceType.ALCOHOL].stock = 0.8
    agents["Addicted Agent"].addiction_states[SubstanceType.ALCOHOL].withdrawal_severity = 0.6
    agents["Addicted Agent"].habit_stocks[BehaviorType.DRINKING] = 0.9
    
    agents["Stressed Agent"].internal_state.stress = 0.8
    agents["Stressed Agent"].internal_state.wealth = 300.0
    agents["Stressed Agent"].internal_state.monthly_expenses = 800.0
    
    base_intensity = 0.5
    
    print("Alcohol Cue Modulation (base intensity: 0.5):")
    for name, agent in agents.items():
        modulated = cue_generator._apply_agent_state_modulation(
            base_intensity, CueType.ALCOHOL_CUE, agent
        )
        print(f"  {name:15} → {modulated:6.4f}")
    
    print("\nGambling Cue Modulation (base intensity: 0.5):")
    for name, agent in agents.items():
        modulated = cue_generator._apply_agent_state_modulation(
            base_intensity, CueType.GAMBLING_CUE, agent
        )
        print(f"  {name:15} → {modulated:6.4f}")
    
    print()


def demonstrate_temporal_cues():
    """Demonstrate temporal cue generation."""
    print("=== Temporal Cues ===")
    
    cue_generator = CueGenerator()
    
    # Create vulnerable agent
    agent = Agent.create_with_profile('vulnerable')
    agent.internal_state.wealth = 200.0
    agent.internal_state.monthly_expenses = 800.0
    agent.addiction_states[SubstanceType.ALCOHOL].withdrawal_severity = 0.7
    agent.habit_stocks[BehaviorType.DRINKING] = 0.8
    
    # Test different times of month
    times = [
        ("Early month", 0.2),
        ("Mid month", 0.5),
        ("Late month", 0.8),
        ("End of month", 0.95)
    ]
    
    for time_name, progress in times:
        time = SimulationTime()
        time.month_progress = progress
        
        cues = cue_generator.generate_temporal_cues(agent, time)
        
        print(f"{time_name:12} ({progress:4.2f}): {len(cues)} cues")
        for cue in cues:
            print(f"  - {cue.cue_type.name}: {cue.intensity:.3f}")
    
    print()


def demonstrate_social_cues():
    """Demonstrate social cue generation."""
    print("=== Social Cues ===")
    
    cue_generator = CueGenerator()
    
    # Create observer agent
    observer = Agent.create_with_profile('balanced')
    
    # Create agents with different habit levels
    agents = [
        ("Light drinker", Agent.create_with_profile('cautious')),
        ("Heavy drinker", Agent.create_with_profile('vulnerable')),
        ("Problem gambler", Agent.create_with_profile('impulsive'))
    ]
    
    # Set habit levels
    agents[1][1].habit_stocks[BehaviorType.DRINKING] = 0.9
    agents[2][1].habit_stocks[BehaviorType.GAMBLING] = 0.8
    
    nearby_agents = [agent for _, agent in agents]
    
    cues = cue_generator.generate_social_cues(observer, nearby_agents)
    
    print(f"Observer receives {len(cues)} social cues:")
    for cue in cues:
        print(f"  - {cue.cue_type.name}: {cue.intensity:.3f}")
    
    print()


def demonstrate_combined_scenario():
    """Demonstrate a complex scenario with multiple cue types."""
    print("=== Combined Scenario: Vulnerable Agent in High-Risk Environment ===")
    
    cue_generator = CueGenerator()
    
    # Create highly vulnerable agent
    agent = Agent.create_with_profile('vulnerable')
    agent.internal_state.wealth = 150.0
    agent.internal_state.monthly_expenses = 800.0
    agent.internal_state.stress = 0.9
    agent.addiction_states[SubstanceType.ALCOHOL].stock = 0.8
    agent.addiction_states[SubstanceType.ALCOHOL].withdrawal_severity = 0.7
    agent.habit_stocks[BehaviorType.DRINKING] = 0.9
    agent.habit_stocks[BehaviorType.GAMBLING] = 0.6
    
    print("Agent State:")
    print(f"  Wealth: ${agent.internal_state.wealth:.0f} (expenses: ${agent.internal_state.monthly_expenses:.0f})")
    print(f"  Stress: {agent.internal_state.stress:.2f}")
    print(f"  Alcohol addiction: {agent.addiction_states[SubstanceType.ALCOHOL].stock:.2f}")
    print(f"  Withdrawal severity: {agent.addiction_states[SubstanceType.ALCOHOL].withdrawal_severity:.2f}")
    print(f"  Drinking habit: {agent.habit_stocks[BehaviorType.DRINKING]:.2f}")
    print(f"  Gambling habit: {agent.habit_stocks[BehaviorType.GAMBLING]:.2f}")
    
    # Test temporal cues at end of month
    time = SimulationTime()
    time.month_progress = 0.9
    
    temporal_cues = cue_generator.generate_temporal_cues(agent, time)
    
    print(f"\nTemporal Cues (end of month): {len(temporal_cues)}")
    for cue in temporal_cues:
        print(f"  - {cue.cue_type.name}: {cue.intensity:.3f}")
    
    # Test how spatial cues would be modulated
    print(f"\nSpatial Cue Modulation Examples:")
    base_intensities = {
        CueType.ALCOHOL_CUE: 0.6,
        CueType.GAMBLING_CUE: 0.5,
        CueType.FINANCIAL_STRESS_CUE: 0.4
    }
    
    for cue_type, base_intensity in base_intensities.items():
        modulated = cue_generator._apply_agent_state_modulation(
            base_intensity, cue_type, agent
        )
        amplification = modulated / base_intensity
        print(f"  {cue_type.name:20}: {base_intensity:.2f} → {modulated:.3f} ({amplification:.1f}x)")
    
    print()


def main():
    """Run all demonstrations."""
    print("Environmental Cue System Demonstration")
    print("=" * 50)
    print()
    
    demonstrate_distance_based_intensity()
    demonstrate_agent_state_modulation()
    demonstrate_temporal_cues()
    demonstrate_social_cues()
    demonstrate_combined_scenario()
    
    print("Demonstration complete!")
    print("\nKey Insights:")
    print("1. Cue intensity decreases realistically with distance")
    print("2. Agent addiction/habit states amplify relevant cues")
    print("3. Temporal factors (like end-of-month stress) generate additional cues")
    print("4. Social modeling creates weak cues from observing others")
    print("5. Vulnerable agents experience much stronger cue effects")


if __name__ == "__main__":
    main() 
