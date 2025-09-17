"""Tests for the visualization template library."""

from __future__ import annotations

import pytest

from simulacra.visualization.template_library import TemplateManager


@pytest.fixture()
def template_manager() -> TemplateManager:
    """Provide a fresh template manager for each test."""
    return TemplateManager()


@pytest.mark.parametrize(
    ("template_id", "expected"),
    [
        (
            "basic_urban",
            {"city_name": "Basic Urban Study", "total_agents": 50, "duration_months": 6},
        ),
        (
            "addiction_research",
            {
                "city_name": "Addiction Research Study",
                "total_agents": 100,
                "duration_months": 18,
            },
        ),
        (
            "economic_inequality",
            {
                "city_name": "Economic Inequality Study",
                "total_agents": 150,
                "duration_months": 24,
            },
        ),
        (
            "policy_testing",
            {
                "city_name": "Policy Testing Environment",
                "total_agents": 200,
                "duration_months": 12,
            },
        ),
    ],
)
def test_template_configurations_apply_overrides(
    template_manager: TemplateManager, template_id: str, expected: dict[str, int | str]
) -> None:
    """Templates should expose the intended configuration defaults."""
    template = template_manager.get_template(template_id)
    assert template is not None

    configuration = template["configuration"]
    assert configuration["city_name"] == expected["city_name"]
    assert configuration["total_agents"] == expected["total_agents"]
    assert configuration["duration_months"] == expected["duration_months"]
