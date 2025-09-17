"""Project persistence utilities for the unified visualization interface."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .configuration import SimulationConfiguration


@dataclass
class Project:
    """Container for a persisted simulation project."""

    id: str
    configuration: SimulationConfiguration
    status: str = "configured"
    simulation_id: Optional[str] = None
    results_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the project for disk storage."""
        return {
            "id": self.id,
            "configuration": self.configuration.to_dict(),
            "status": self.status,
            "simulation_id": self.simulation_id,
            "results_path": str(self.results_path) if self.results_path else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Rehydrate a project from JSON data."""
        configuration = SimulationConfiguration.from_dict(data["configuration"])
        results_path = data.get("results_path")
        return cls(
            id=data["id"],
            configuration=configuration,
            status=data.get("status", "configured"),
            simulation_id=data.get("simulation_id"),
            results_path=Path(results_path) if results_path else None,
        )


@dataclass
class ProjectManager:
    """Manage creation and storage of simulation projects."""

    projects_dir: Path = field(default_factory=lambda: Path("simulacra_projects"))

    def __post_init__(self) -> None:
        self.projects_dir.mkdir(exist_ok=True)
        self._projects: Dict[str, Project] = {}
        self._load_existing_projects()

    def create_project(self, config_data: Dict[str, Any]) -> Project:
        """Create and persist a new project from configuration data."""
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        configuration = SimulationConfiguration.from_dict(config_data)
        configuration.project_id = project_id
        configuration.created_at = datetime.now()

        project = Project(id=project_id, configuration=configuration)
        self._projects[project_id] = project
        self._save_project(project)
        return project

    def list_projects(self) -> Iterable[Dict[str, Any]]:
        """Return lightweight metadata for all known projects."""
        for project in self._projects.values():
            yield {
                "id": project.id,
                "name": project.configuration.city_name,
                "created_at": (
                    project.configuration.created_at.isoformat()
                    if project.configuration.created_at
                    else None
                ),
                "agents": project.configuration.total_agents,
                "duration": project.configuration.duration_months,
                "status": project.status,
            }

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by identifier."""
        return self._projects.get(project_id)

    def _load_existing_projects(self) -> None:
        """Read all JSON project files from disk."""
        for project_file in self.projects_dir.glob("*.json"):
            try:
                data = json.loads(project_file.read_text())
            except json.JSONDecodeError:
                continue
            project = Project.from_dict(data)
            self._projects[project.id] = project

    def _save_project(self, project: Project) -> None:
        """Persist a single project to disk."""
        project_file = self.projects_dir / f"{project.id}.json"
        project_file.write_text(json.dumps(project.to_dict(), indent=2, default=str))
