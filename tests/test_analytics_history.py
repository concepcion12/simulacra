"""Tests for analytics history utilities."""

from datetime import datetime

import pytest

from simulacra.analytics.history import (
    HistoryTracker,
    StateSnapshot,
    EventType,
)
from simulacra.agents.agent import Agent
from simulacra.utils.types import EmploymentInfo, HousingInfo


def test_state_snapshot_handles_employment_and_budget() -> None:
    """State snapshots should use valid employment and action budget data."""
    agent = Agent(initial_wealth=5000.0)
    agent.employment = EmploymentInfo(base_salary=2500.0)
    agent.employment.performance_history.average_performance = 0.8
    agent.home = HousingInfo(monthly_rent=1200.0)

    agent.action_budget.spend(10.0)

    snapshot = StateSnapshot.from_agent(agent, datetime.utcnow())

    performance = agent.employment.performance_history.average_performance
    expected_income = agent.employment.base_salary * performance
    assert snapshot.monthly_income == pytest.approx(expected_income)
    assert snapshot.actions_taken_this_month == agent.action_budget.actions_taken
    remaining_hours = agent.action_budget.remaining_hours
    assert snapshot.time_budget_remaining == pytest.approx(remaining_hours)


def test_record_life_event_returns_event() -> None:
    """record_life_event should return the created event for tracked agents."""
    tracker = HistoryTracker()
    agent = Agent()
    timestamp = datetime.utcnow()
    tracker.register_agent(agent, timestamp)

    event = tracker.record_life_event(
        agent.id,
        EventType.WINDFALL,
        "Won a prize",
        timestamp,
        wealth_impact=5000.0,
    )

    assert event is not None
    assert event.event_type is EventType.WINDFALL
    assert tracker.agent_histories[agent.id].life_events[-1] is event


def test_detect_life_events_returns_events() -> None:
    """detect_life_events should return the events that were recorded."""
    tracker = HistoryTracker()
    agent = Agent()
    timestamp = datetime.utcnow()
    tracker.register_agent(agent, timestamp)

    pre_state = {'employed': False, 'wealth': 100.0}
    post_state = {
        'employed': True,
        'employer_name': 'Acme Corp',
        'employer_id': 'EMP-1',
        'salary': 1800.0,
        'wealth': 100.0,
    }

    events = tracker.detect_life_events(agent, pre_state, post_state, timestamp)

    assert events
    assert events[0].event_type is EventType.JOB_GAINED
    assert tracker.agent_histories[agent.id].life_events[-1].event_type is EventType.JOB_GAINED
