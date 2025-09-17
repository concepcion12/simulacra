"""Template catalog for ready-made simulation scenarios."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .configuration import SimulationConfiguration


class TemplateManager:
    """Provide a curated set of starter configurations for the UI."""

    def __init__(self) -> None:
        self.templates = self._create_default_templates()

    def _create_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create the default template library."""
        templates: Dict[str, Dict[str, Any]] = {}

        def build_template(
            template_id: str,
            name: str,
            description: str,
            category: str,
            overrides: Dict[str, Any],
            tags: list[str],
        ) -> Dict[str, Any]:
            configuration = SimulationConfiguration.from_dict(overrides)
            return {
                "id": template_id,
                "name": name,
                "description": description,
                "category": category,
                "configuration": configuration.to_dict(),
                "tags": tags,
            }

        templates["basic_urban"] = build_template(
            "basic_urban",
            "Basic Urban Study",
            "Simple urban simulation for learning and basic research",
            "basic",
            {
                "city_name": "Basic Urban Study",
                "total_agents": 50,
                "duration_months": 6,
                "population_mix": {"balanced": 0.8, "vulnerable": 0.2},
            },
            ["beginner", "education", "general"],
        )

        templates["addiction_research"] = build_template(
            "addiction_research",
            "Addiction Research",
            "Study addiction patterns and intervention effectiveness",
            "addiction",
            {
                "city_name": "Addiction Research Study",
                "total_agents": 100,
                "duration_months": 18,
                "population_mix": {"balanced": 0.5, "vulnerable": 0.5},
                "buildings": {
                    "residential": 15,
                    "commercial": 8,
                    "liquor_stores": 6,
                    "casinos": 3,
                },
                "behavioral_params": {
                    "risk_preference": "normal",
                    "addiction_vulnerability": 0.6,
                    "economic_stress": 0.5,
                    "impulsivity_range": [0.2, 0.8],
                },
            },
            ["addiction", "healthcare", "research"],
        )

        templates["economic_inequality"] = build_template(
            "economic_inequality",
            "Economic Inequality",
            "Examine wealth distribution and economic mobility",
            "economic",
            {
                "city_name": "Economic Inequality Study",
                "total_agents": 150,
                "duration_months": 24,
                "population_mix": {
                    "wealthy": 0.1,
                    "middle_class": 0.3,
                    "working_class": 0.4,
                    "poor": 0.2,
                },
                "economic_conditions": {
                    "unemployment_rate": 0.12,
                    "rent_inflation": 0.02,
                    "economic_shocks": "mild",
                    "job_market": "balanced",
                },
            },
            ["economics", "inequality", "policy"],
        )

        templates["policy_testing"] = build_template(
            "policy_testing",
            "Policy Testing",
            "Test policy interventions and their effectiveness",
            "policy",
            {
                "city_name": "Policy Testing Environment",
                "total_agents": 200,
                "duration_months": 12,
                "population_mix": {
                    "balanced": 0.6,
                    "vulnerable": 0.3,
                    "resilient": 0.1,
                },
            },
            ["policy", "government", "intervention"],
        )

        return templates

    def list_templates(self) -> list[Dict[str, Any]]:
        """Return the available templates as dictionaries."""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single template by identifier."""
        return self.templates.get(template_id)
