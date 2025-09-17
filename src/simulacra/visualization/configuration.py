"""Simulation configuration models for the unified interface."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class SimulationConfiguration:
    """Structured representation of the unified interface configuration state."""

    city_name: str = "New City"
    city_size: str = "medium"
    districts: list[dict[str, Any]] | list[str] | None = None
    buildings: Dict[str, int] | None = None
    total_agents: int = 100
    population_mix: Dict[str, float] | None = None
    behavioral_params: Dict[str, Any] | None = None
    duration_months: int = 12
    rounds_per_month: int = 8
    update_interval: float = 1.0
    economic_conditions: Dict[str, Any] | None = None
    data_collection: Dict[str, bool] | None = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    project_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialise default dictionaries and coerce stored timestamps."""
        if self.districts is None:
            self.districts = []
        if self.buildings is None:
            self.buildings = {
                "residential": 10,
                "commercial": 5,
                "industrial": 3,
                "casinos": 2,
                "liquor_stores": 5,
            }
        if self.population_mix is None:
            self.population_mix = {"balanced": 0.7, "vulnerable": 0.3}
        if self.behavioral_params is None:
            self.behavioral_params = {
                "risk_preference": "normal",
                "addiction_vulnerability": 0.4,
                "economic_stress": 0.5,
                "impulsivity_range": [0.2, 0.8],
            }
        if self.economic_conditions is None:
            self.economic_conditions = {
                "unemployment_rate": 0.08,
                "rent_inflation": 0.02,
                "economic_shocks": "mild",
                "job_market": "balanced",
            }
        if self.data_collection is None:
            self.data_collection = {
                "agent_metrics": True,
                "population_stats": True,
                "life_events": True,
                "action_history": True,
                "export_data": True,
            }

        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.modified_at, str):
            self.modified_at = datetime.fromisoformat(self.modified_at)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the configuration for JSON storage."""
        return {
            "city_name": self.city_name,
            "city_size": self.city_size,
            "districts": self.districts,
            "buildings": self.buildings,
            "total_agents": self.total_agents,
            "population_mix": self.population_mix,
            "behavioral_params": self.behavioral_params,
            "duration_months": self.duration_months,
            "rounds_per_month": self.rounds_per_month,
            "update_interval": self.update_interval,
            "economic_conditions": self.economic_conditions,
            "data_collection": self.data_collection,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "project_id": self.project_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfiguration":
        """Create a configuration instance from stored dictionary data."""
        return cls(**data)

    def validate(self) -> Dict[str, Any]:
        """Validate the configuration and return structured error messages."""
        errors: list[str] = []
        warnings: list[str] = []

        if not self.city_name or not self.city_name.strip():
            errors.append("City name is required")

        if self.total_agents < 1:
            errors.append("Must have at least 1 agent")
        elif self.total_agents > 1000:
            warnings.append("Large populations (>1000) may cause performance issues")

        if isinstance(self.population_mix, dict):
            mix_sum = sum(self.population_mix.values())
            if abs(mix_sum - 1.0) > 0.01:
                errors.append(
                    f"Population mix must sum to 1.0, currently sums to {mix_sum:.2f}"
                )

        total_housing = self.buildings.get("residential", 0) * 5
        if total_housing < self.total_agents:
            warnings.append(
                "Insufficient housing capacity "
                f"({total_housing}) for population ({self.total_agents})"
            )

        return {"valid": not errors, "errors": errors, "warnings": warnings}
