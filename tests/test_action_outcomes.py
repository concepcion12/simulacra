"""Regression tests for action outcome generation and updates."""

from simulacra.agents.action_outcomes import (
    ActionOutcomeGenerator,
    OutcomeContext,
    StateUpdater,
)
from simulacra.agents.agent import Agent
from simulacra.agents.decision_making import Action
from simulacra.utils.types import (
    ActionType,
    EmploymentInfo,
    GamblingOutcome,
    RestOutcome,
    WorkOutcome,
)


def _create_agent(profile: str = "balanced", wealth: float = 1000.0) -> Agent:
    """Create a test agent with configurable starting wealth."""
    return Agent.create_with_profile(profile, initial_wealth=wealth)


def test_work_requires_employment() -> None:
    """Agents without employment should receive a failed work outcome."""
    agent = _create_agent()
    generator = ActionOutcomeGenerator(random_seed=1)
    action = Action(ActionType.WORK, 8.0)

    outcome = generator.generate_outcome(agent, action, OutcomeContext())

    assert isinstance(outcome, WorkOutcome)
    assert not outcome.success
    assert outcome.payment == 0.0
    assert "employment" in outcome.message.lower()


def test_gambling_requires_sufficient_funds() -> None:
    """Gambling outcomes should fail when the agent cannot cover the bet."""
    agent = _create_agent(wealth=20.0)
    generator = ActionOutcomeGenerator(random_seed=2)
    action = Action(ActionType.GAMBLE, 2.0, parameters={"bet_amount": 50.0})

    outcome = generator.generate_outcome(agent, action, OutcomeContext())

    assert isinstance(outcome, GamblingOutcome)
    assert not outcome.success
    assert outcome.monetary_change == 0.0
    assert "insufficient" in outcome.message.lower()


def test_rest_outcome_updates_internal_state() -> None:
    """Rest outcomes should reduce stress and restore self-control."""
    agent = _create_agent()
    agent.internal_state.stress = 0.8
    agent.internal_state.mood = -0.2
    agent.internal_state.self_control_resource = 0.3

    generator = ActionOutcomeGenerator(random_seed=3)
    action = Action(ActionType.REST, 4.0)
    context = OutcomeContext(location_quality=0.9)

    outcome = generator.generate_outcome(agent, action, context)
    assert isinstance(outcome, RestOutcome)

    StateUpdater().apply_outcome(agent, outcome)

    assert agent.internal_state.stress < 0.8
    assert agent.internal_state.self_control_resource >= 0.3
    assert agent.internal_state.mood > -0.2


def test_work_outcome_increases_wealth() -> None:
    """Successful work outcomes should add earnings to the agent's wealth."""
    agent = _create_agent()
    agent.employment = EmploymentInfo(job_quality=0.7, base_salary=2400.0)

    generator = ActionOutcomeGenerator(random_seed=4)
    action = Action(ActionType.WORK, 8.0)

    initial_wealth = agent.internal_state.wealth
    outcome = generator.generate_outcome(agent, action, OutcomeContext())
    assert outcome.success

    StateUpdater().apply_outcome(agent, outcome)

    assert agent.internal_state.wealth > initial_wealth
    assert agent.internal_state.stress >= 0.0
