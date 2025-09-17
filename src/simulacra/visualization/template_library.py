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

        basic_config = SimulationConfiguration(
            {
                "city_name": "Basic Urban Study",
                "total_agents": 50,
                "duration_months": 6,
                "population_mix": {"balanced": 0.8, "vulnerable": 0.2},
            }
        )
        templates["basic_urban"] = {
            "id": "basic_urban",
            "name": "Basic Urban Study",
            "description": "Simple urban simulation for learning and basic research",
            "category": "basic",
            "configuration": basic_config.to_dict(),
            "tags": ["beginner", "education", "general"],
        }

        addiction_config = SimulationConfiguration(
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
            }
        )
        templates["addiction_research"] = {
            "id": "addiction_research",
            "name": "Addiction Research",
            "description": "Study addiction patterns and intervention effectiveness",
            "category": "addiction",
            "configuration": addiction_config.to_dict(),
            "tags": ["addiction", "healthcare", "research"],
        }

        economic_config = SimulationConfiguration(
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
            }
        )
        templates["economic_inequality"] = {
            "id": "economic_inequality",
            "name": "Economic Inequality",
            "description": "Examine wealth distribution and economic mobility",
            "category": "economic",
            "configuration": economic_config.to_dict(),
            "tags": ["economics", "inequality", "policy"],
        }

        policy_config = SimulationConfiguration(
            {
                "city_name": "Policy Testing Environment",
                "total_agents": 200,
                "duration_months": 12,
                "population_mix": {
                    "balanced": 0.6,
                    "vulnerable": 0.3,
                    "resilient": 0.1,
                },
            }
        )
        templates["policy_testing"] = {
            "id": "policy_testing",
            "name": "Policy Testing",
            "description": "Test policy interventions and their effectiveness",
            "category": "policy",
            "configuration": policy_config.to_dict(),
            "tags": ["policy", "government", "intervention"],
        }

        return templates

    def list_templates(self) -> list[Dict[str, Any]]:
        """Return the available templates as dictionaries."""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single template by identifier."""
        return self.templates.get(template_id)
