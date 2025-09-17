"""Tests covering core agent construction and foundational mechanics."""
from __future__ import annotations

import math

from simulacra.agents import Agent
from simulacra.utils.types import (
    ActionBudget,
    BehaviorType,
    FinancialStressCue,
    SubstanceType,
    AlcoholCue,
    GamblingCue,
)


def test_agent_profile_traits_are_configured() -> None:
    """Predefined profiles should produce predictable personality traits."""
    cautious = Agent.create_with_profile("cautious", initial_wealth=1500.0)

    assert math.isclose(cautious.personality.baseline_impulsivity, 0.2)
    assert math.isclose(cautious.personality.cognitive_type, 0.8)
    assert math.isclose(cautious.personality.addiction_vulnerability, 0.1)


def test_update_internal_states_adjusts_cravings() -> None:
    """Addiction progression should increase withdrawal and craving over time."""
    agent = Agent.create_with_profile("vulnerable", initial_wealth=500.0)
    alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
    alcohol_state.stock = 0.6
    alcohol_state.time_since_last_use = 3

    agent.update_internal_states(delta_time=1)

    assert alcohol_state.withdrawal_severity > 0
    assert agent.craving_intensities[SubstanceType.ALCOHOL] > 0


def test_process_environmental_cues_increases_pressure() -> None:
    """Environmental cues should raise the relevant craving and stress levels."""
    agent = Agent.create_with_profile("balanced")
    agent.addiction_states[SubstanceType.ALCOHOL].stock = 0.4
    agent.craving_intensities[SubstanceType.ALCOHOL] = 0.2
    agent.habit_stocks[BehaviorType.GAMBLING] = 0.5
    agent.craving_intensities[BehaviorType.GAMBLING] = 0.15
    initial_alcohol_craving = agent.craving_intensities[SubstanceType.ALCOHOL]
    initial_gambling_craving = agent.craving_intensities[BehaviorType.GAMBLING]
    initial_stress = agent.internal_state.stress

    cues = [
        AlcoholCue(intensity=0.7),
        GamblingCue(intensity=0.6),
        FinancialStressCue(intensity=0.8),
    ]
    agent.process_environmental_cues(cues)

    assert agent.craving_intensities[SubstanceType.ALCOHOL] > initial_alcohol_craving
    assert agent.craving_intensities[BehaviorType.GAMBLING] > initial_gambling_craving
    assert agent.internal_state.stress > initial_stress


def test_behavioral_modules_reflect_temporal_discounting() -> None:
    """Future rewards should be discounted more heavily as delay grows."""
    agent = Agent.create_with_profile("impulsive")
    future_utility = 100.0

    immediate = agent.temporal_discounting.discount_future_utility(
        future_utility,
        delay=0,
        personality=agent.personality,
        cognitive_load=0.1,
        craving_intensity=0.2,
    )
    delayed = agent.temporal_discounting.discount_future_utility(
        future_utility,
        delay=6,
        personality=agent.personality,
        cognitive_load=0.1,
        craving_intensity=0.2,
    )

    assert immediate > delayed


def test_action_budget_spend_and_reset() -> None:
    """The action budget should prevent overspending and reset cleanly."""
    budget = ActionBudget(total_hours=40.0)

    assert budget.can_afford(10.0)
    budget.spend(10.0)
    assert math.isclose(budget.remaining_hours, 30.0)
    assert not budget.can_afford(40.0)

    budget.reset()
    assert math.isclose(budget.remaining_hours, 40.0)
