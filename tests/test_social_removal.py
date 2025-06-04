"""Validate that social components have been removed from the code base."""

import pytest


def test_social_removal():
    """Check that no social functionality remains."""
    from src.utils.types import ActionType, UtilityWeights

    # ActionType should not contain any social actions
    socialize_actions = [action for action in ActionType if 'SOCIAL' in action.name]
    assert not socialize_actions

    # Importing SocializeOutcome should fail
    with pytest.raises(ImportError):
        from src.utils.types import SocializeOutcome  # noqa: F401

    from src.agents.agent import Agent
    agent = Agent()
    assert not hasattr(agent, 'social_connections')

    weights = UtilityWeights()
    assert not hasattr(weights, 'social')
