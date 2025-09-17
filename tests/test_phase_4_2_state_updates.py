"""Tests covering detailed state updates from action outcomes."""
from __future__ import annotations

import numpy as np

from simulacra.agents.agent import Agent
from simulacra.agents.decision_making import Action
from simulacra.agents.action_outcomes import ActionOutcomeGenerator, StateUpdater
from simulacra.utils.types import (
    ActionType,
    WorkOutcome,
    GamblingOutcome,
    JobSearchOutcome,
    HousingSearchOutcome,
    EmploymentInfo,
)


class TestWorkPerformanceTracking:
    """Verify that employment performance history is persisted correctly."""

    def test_performance_history_tracking(self) -> None:
        agent = Agent.create_with_profile("balanced")
        agent.employment = EmploymentInfo(job_quality=0.7, base_salary=2500.0)
        state_updater = StateUpdater()

        performances = [0.8, 0.9, 0.7, 1.0, 0.85]
        for performance in performances:
            state_updater.apply_outcome(
                agent,
                WorkOutcome(
                    success=True,
                    payment=500.0,
                    performance=performance,
                    stress_increase=0.05,
                ),
            )

        history = agent.employment.performance_history
        assert len(history.recent_performances) == len(performances)
        assert history.months_employed == len(performances)
        assert abs(history.average_performance - np.mean(performances)) < 0.01

    def test_performance_warnings_increment(self) -> None:
        agent = Agent.create_with_profile("balanced")
        agent.employment = EmploymentInfo()
        state_updater = StateUpdater()

        state_updater.apply_outcome(
            agent,
            WorkOutcome(
                success=True,
                payment=300.0,
                performance=0.4,
                stress_increase=0.1,
            ),
        )

        assert agent.employment.performance_history.warnings_received == 1


class TestGamblingTracking:
    """Ensure gambling statistics correctly capture wins, losses, and streaks."""

    def test_gambling_statistics_tracking(self) -> None:
        agent = Agent.create_with_profile("impulsive", initial_wealth=500.0)
        state_updater = StateUpdater()

        outcomes = [
            GamblingOutcome(success=True, monetary_change=50.0),
            GamblingOutcome(success=True, monetary_change=-30.0),
            GamblingOutcome(success=True, monetary_change=-20.0),
            GamblingOutcome(success=True, monetary_change=40.0),
        ]
        for outcome in outcomes:
            state_updater.apply_outcome(agent, outcome)

        context = agent.gambling_context
        assert context.total_games == len(outcomes)
        assert context.total_wins == 90.0
        assert context.total_losses == 50.0
        assert context.loss_streak == 0

    def test_loss_streak_captures_failed_bet(self) -> None:
        agent = Agent.create_with_profile("impulsive")
        outcome_generator = ActionOutcomeGenerator(random_seed=42)

        action = Action(ActionType.GAMBLE, 2.0, parameters={"bet_amount": 10_000.0})
        outcome = outcome_generator.generate_outcome(agent, action)

        assert not outcome.success


class TestJobHousingAssignment:
    """Check that job and housing search outcomes mutate agent state properly."""

    def test_job_assignment_creates_employment_info(self) -> None:
        agent = Agent.create_with_profile("balanced")
        state_updater = StateUpdater()

        assert agent.employment is None

        state_updater.apply_outcome(
            agent,
            JobSearchOutcome(
                success=True,
                job_found=True,
                job_quality=0.7,
                stress_change=-0.1,
            ),
        )

        assert agent.employment is not None
        assert agent.employment.job_quality == 0.7
        assert agent.employment.base_salary > 0
        assert agent.employment.performance_history is not None

    def test_housing_assignment_creates_housing_info(self) -> None:
        agent = Agent.create_with_profile("balanced")
        state_updater = StateUpdater()

        assert agent.home is None

        state_updater.apply_outcome(
            agent,
            HousingSearchOutcome(
                success=True,
                housing_found=True,
                housing_quality=0.6,
                rent_cost=800.0,
            ),
        )

        assert agent.home is not None
        assert agent.home.housing_quality == 0.6
        assert agent.home.monthly_rent == 800.0

    def test_employment_adjusts_monthly_expenses(self) -> None:
        agent = Agent.create_with_profile("balanced")
        state_updater = StateUpdater()
        initial_expenses = agent.internal_state.monthly_expenses

        state_updater.apply_outcome(
            agent,
            JobSearchOutcome(
                success=True,
                job_found=True,
                job_quality=0.9,
                stress_change=-0.1,
            ),
        )

        assert agent.internal_state.monthly_expenses > initial_expenses
