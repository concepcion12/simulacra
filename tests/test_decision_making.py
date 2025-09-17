"""Unit tests for the behavioral decision-making system."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pytest

from simulacra.agents import Agent, Action, ActionContext, generate_available_actions
from simulacra.utils.types import (
    ActionType,
    BehaviorType,
    SubstanceType,
    EmploymentInfo,
)


@pytest.fixture(autouse=True)
def _seed_random() -> None:
    """Seed numpy's RNG for deterministic probabilistic choices."""
    np.random.seed(42)


@pytest.fixture
def baseline_agent() -> Agent:
    """Return a balanced agent with a replenished action budget."""
    agent = Agent.create_with_profile("balanced", initial_wealth=1200.0)
    agent.action_budget.reset()
    return agent


def _action_probabilities(agent: Agent, actions: list[Action]) -> Dict[ActionType, float]:
    """Helper to compute a mapping of action type to probability."""
    context = ActionContext(agent=agent)
    probability_pairs = agent.decision_maker.get_action_probabilities(agent, actions, context)
    return {action.action_type: prob for action, prob in probability_pairs}


def test_generate_available_actions_always_offers_rest(baseline_agent: Agent) -> None:
    """Agents with remaining budget should always be able to rest."""
    context = ActionContext(agent=baseline_agent)
    actions = generate_available_actions(baseline_agent, context)
    action_types = {action.action_type for action in actions}

    assert ActionType.REST in action_types


def test_generate_available_actions_respects_budget(baseline_agent: Agent) -> None:
    """Spending the entire budget removes time-intensive options such as rest."""
    baseline_agent.action_budget.spend(baseline_agent.action_budget.total_hours)
    context = ActionContext(agent=baseline_agent)
    actions = generate_available_actions(baseline_agent, context)

    assert all(action.action_type != ActionType.REST for action in actions)


def test_addiction_component_rewards_relief() -> None:
    """Addiction relief should increase the utility of alcohol consumption."""
    agent = Agent.create_with_profile("vulnerable", initial_wealth=500.0)
    alcohol_state = agent.addiction_states[SubstanceType.ALCOHOL]
    alcohol_state.stock = 0.7
    alcohol_state.withdrawal_severity = 0.6
    agent.craving_intensities[SubstanceType.ALCOHOL] = 0.8

    action = Action(ActionType.DRINK, time_cost=2.0, parameters={"units": 2})
    total, components = agent.decision_maker.utility_calculator.calculate_total_utility(
        action,
        agent,
        ActionContext(agent=agent),
    )

    assert components["addiction"] > 0
    assert components["financial"] < 0
    assert total > 0  # Relief outweighs the financial penalty under heavy craving


def test_work_financial_utility_exceeds_begging() -> None:
    """Working with a stable job should provide more utility than begging."""
    agent = Agent.create_with_profile("balanced", initial_wealth=800.0)
    employment = EmploymentInfo(job_quality=0.7, base_salary=2500.0)
    employment.job = type("MockJob", (), {"monthly_salary": 2200.0, "stress_level": 0.2})()
    agent.employment = employment

    work = Action(ActionType.WORK, time_cost=160.0)
    beg = Action(ActionType.BEG, time_cost=8.0)
    context = ActionContext(agent=agent)

    work_total, _ = agent.decision_maker.utility_calculator.calculate_total_utility(
        work,
        agent,
        context,
    )
    beg_total, _ = agent.decision_maker.utility_calculator.calculate_total_utility(
        beg,
        agent,
        context,
    )

    assert work_total > beg_total


def test_dual_process_theta_reacts_to_stress(baseline_agent: Agent) -> None:
    """High stress and craving should reduce System 2 influence."""
    decision_maker = baseline_agent.decision_maker
    theta_base = decision_maker._calculate_effective_theta(baseline_agent)

    baseline_agent.internal_state.self_control_resource = 0.3
    baseline_agent.internal_state.cognitive_load = 0.4
    baseline_agent.internal_state.stress = 0.9
    baseline_agent.craving_intensities[SubstanceType.ALCOHOL] = 0.85

    theta_stressed = decision_maker._calculate_effective_theta(baseline_agent)

    assert theta_stressed < theta_base
    assert theta_stressed >= 0.1  # Guardrail from implementation


def test_craving_shifts_action_preferences() -> None:
    """Increasing craving raises the probability of drinking over resting."""
    agent = Agent.create_with_profile("vulnerable", initial_wealth=400.0)
    rest_action = Action(ActionType.REST, time_cost=4.0)
    drink_action = Action(ActionType.DRINK, time_cost=2.0, parameters={"units": 2})

    low_craving_probs = _action_probabilities(agent, [rest_action, drink_action])
    low_rest = low_craving_probs[ActionType.REST]
    low_drink = low_craving_probs[ActionType.DRINK]

    agent.craving_intensities[SubstanceType.ALCOHOL] = 0.9
    agent.addiction_states[SubstanceType.ALCOHOL].withdrawal_severity = 0.5
    agent.habit_stocks[BehaviorType.DRINKING] = 0.6

    high_craving_probs = _action_probabilities(agent, [rest_action, drink_action])
    high_rest = high_craving_probs[ActionType.REST]
    high_drink = high_craving_probs[ActionType.DRINK]

    assert pytest.approx(low_rest + low_drink, rel=1e-6) == 1.0
    assert pytest.approx(high_rest + high_drink, rel=1e-6) == 1.0
    assert high_drink > low_drink
    assert high_rest < low_rest
