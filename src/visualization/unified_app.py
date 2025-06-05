"""
Enhanced Flask application for unified Simulacra interface.
Extends existing visualization_server.py capabilities with complete workflow support.
"""

import os
import json
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    from flask import Flask, render_template, jsonify, request, session
    from flask_socketio import SocketIO, emit
except ImportError:
    Flask = None
    SocketIO = None
    print(
        "Warning: Flask and flask-socketio not installed. Install with: pip install flask flask-socketio"
    )

from .data_streamer import DataStreamer
from .visualization_server import VisualizationServer
from .simulation_bridge import SimulationBridge


class ProjectManager:
    """Manages simulation projects and their configurations."""

    def __init__(self, projects_dir: str = "simulacra_projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        self._projects: Dict[str, "Project"] = {}
        self._load_existing_projects()

    def create_project(self, config_data: Dict[str, Any]) -> "Project":
        """Create a new project from configuration data."""
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config = SimulationConfiguration.from_dict(config_data)
        config.project_id = project_id
        config.created_at = datetime.now()

        project = Project(project_id, config)
        self._projects[project_id] = project
        self._save_project(project)
        return project

    def list_projects(self) -> list[Dict[str, Any]]:
        """List all available projects."""
        return [
            {
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
            for project in self._projects.values()
        ]

    def get_project(self, project_id: str) -> Optional["Project"]:
        """Get specific project by ID."""
        return self._projects.get(project_id)

    def _load_existing_projects(self):
        """Load existing projects from disk."""
        for project_file in self.projects_dir.glob("*.json"):
            try:
                with open(project_file, "r") as f:
                    data = json.load(f)
                    project = Project.from_dict(data)
                    self._projects[project.id] = project
            except Exception as e:
                print(f"Error loading project {project_file}: {e}")

    def _save_project(self, project: "Project"):
        """Save project to disk."""
        project_file = self.projects_dir / f"{project.id}.json"
        with open(project_file, "w") as f:
            json.dump(project.to_dict(), f, indent=2, default=str)


class SimulationConfiguration:
    """Complete simulation configuration state."""

    def __init__(self, data: Dict[str, Any] = None):
        data = data or {}

        # City configuration
        self.city_name = data.get("city_name", "New City")
        self.city_size = data.get("city_size", "medium")  # small, medium, large
        self.districts = data.get("districts", [])
        self.buildings = data.get(
            "buildings",
            {
                "residential": 10,
                "commercial": 5,
                "industrial": 3,
                "casinos": 2,
                "liquor_stores": 5,
            },
        )

        # Population configuration
        self.total_agents = data.get("total_agents", 100)
        self.population_mix = data.get(
            "population_mix", {"balanced": 0.7, "vulnerable": 0.3}
        )
        self.behavioral_params = data.get(
            "behavioral_params",
            {
                "risk_preference": "normal",
                "addiction_vulnerability": 0.4,
                "economic_stress": 0.5,
                "impulsivity_range": [0.2, 0.8],
            },
        )

        # Simulation parameters
        self.duration_months = data.get("duration_months", 12)
        self.rounds_per_month = data.get("rounds_per_month", 8)
        self.update_interval = data.get("update_interval", 1.0)

        self.economic_conditions = data.get(
            "economic_conditions",
            {
                "unemployment_rate": 0.08,
                "rent_inflation": 0.02,
                "economic_shocks": "mild",
                "job_market": "balanced",
            },
        )

        self.data_collection = data.get(
            "data_collection",
            {
                "agent_metrics": True,
                "population_stats": True,
                "life_events": True,
                "action_history": True,
                "export_data": True,
            },
        )

        # Metadata
        self.created_at = data.get("created_at")
        self.modified_at = data.get("modified_at")
        self.project_id = data.get("project_id")

        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.modified_at, str):
            self.modified_at = datetime.fromisoformat(self.modified_at)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
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
        """Create instance from dictionary."""
        return cls(data)

    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.

        Returns:
            Dict with 'valid' boolean and 'errors'/'warnings' lists
        """
        errors = []
        warnings = []

        # Validate city configuration
        if not self.city_name or len(self.city_name.strip()) == 0:
            errors.append("City name is required")

        if self.total_agents < 1:
            errors.append("Must have at least 1 agent")
        elif self.total_agents > 1000:
            warnings.append("Large populations (>1000) may cause performance issues")

        # Validate population mix
        if isinstance(self.population_mix, dict):
            mix_sum = sum(self.population_mix.values())
            if abs(mix_sum - 1.0) > 0.01:
                errors.append(
                    f"Population mix must sum to 1.0, currently sums to {mix_sum:.2f}"
                )

        # Validate building capacity
        total_housing = (
            self.buildings.get("residential", 0) * 5
        )  # Assume 5 units per building
        if total_housing < self.total_agents:
            warnings.append(
                f"Insufficient housing capacity ({total_housing}) for population ({self.total_agents})"
            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


class Project:
    """Represents a simulation project."""

    def __init__(self, project_id: str, configuration: SimulationConfiguration):
        self.id = project_id
        self.configuration = configuration
        self.status = "configured"  # configured, running, completed, error
        self.simulation_id: Optional[str] = None
        self.results_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "configuration": self.configuration.to_dict(),
            "status": self.status,
            "simulation_id": self.simulation_id,
            "results_path": str(self.results_path) if self.results_path else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        config = SimulationConfiguration.from_dict(data["configuration"])
        project = cls(data["id"], config)
        project.status = data.get("status", "configured")
        project.simulation_id = data.get("simulation_id")
        project.results_path = (
            Path(data["results_path"]) if data.get("results_path") else None
        )
        return project


class TemplateManager:
    """Manages simulation templates and presets."""

    def __init__(self):
        self.templates = self._create_default_templates()

    def _create_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create the default template library."""
        templates = {}

        # Basic Urban Study Template
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

        # Addiction Research Template
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

        # Economic Inequality Template
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

        # Policy Testing Template
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
        """Get list of all available templates."""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get specific template by ID."""
        return self.templates.get(template_id)


class SimulationManager:
    """Manages simulation execution and control using SimulationBridge."""

    def __init__(self, socketio=None):
        self.simulation_bridge = SimulationBridge(socketio)

    def start_simulation(self, config: Dict[str, Any]) -> str:
        """Start a new simulation with given configuration."""
        # Create simulation using the bridge
        simulation_id = self.simulation_bridge.create_simulation_from_config(config)

        if simulation_id:
            # Start the simulation
            success = self.simulation_bridge.start_simulation(simulation_id)
            if success:
                return simulation_id
            else:
                return None
        else:
            # Fallback to placeholder if bridge components not available
            simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.simulation_bridge.active_simulations[simulation_id] = {
                "id": simulation_id,
                "config": config,
                "status": "starting",
                "created_at": datetime.now(),
            }
            return simulation_id

    def get_status(self, simulation_id: str) -> Dict[str, Any]:
        """Get simulation status."""
        return self.simulation_bridge.get_simulation_status(simulation_id)

    def export_data(
        self, simulation_id: str, export_type: str, options: Dict[str, Any]
    ) -> Path:
        """Export simulation data."""
        export_path = self.simulation_bridge.export_simulation_data(
            simulation_id, export_type, options
        )

        if export_path:
            return export_path
        else:
            # Fallback to placeholder
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = export_dir / f"{simulation_id}_{export_type}_{timestamp}.json"

            with open(export_path, "w") as f:
                json.dump({"simulation_id": simulation_id, "type": export_type}, f)

            return export_path

    def list_active_simulations(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all active simulations."""
        return self.simulation_bridge.list_active_simulations()


class UnifiedSimulacraApp:
    """
    Enhanced Flask application supporting the complete Simulacra workflow.
    Extends existing visualization_server.py capabilities.
    """

    def __init__(self, port: int = 5000, debug: bool = False):
        if Flask is None:
            raise ImportError(
                "Flask is required. Install with: pip install flask flask-socketio"
            )

        self.app = Flask(
            __name__,
            template_folder=self._get_template_dir(),
            static_folder=self._get_static_dir(),
        )
        self.app.secret_key = os.getenv(
            "SIMULACRA_SECRET_KEY", "simulacra_unified_secret_key"
        )
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.debug = debug

        # State management
        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()
        self.simulation_manager = SimulationManager(self.socketio)

        # Integration with existing visualization server
        self.visualization_server: Optional[VisualizationServer] = None

        self._register_routes()
        self._register_socket_handlers()

    def _get_template_dir(self) -> str:
        """Get the templates directory path."""
        current_dir = Path(__file__).parent
        template_dir = current_dir / "templates"
        template_dir.mkdir(exist_ok=True)
        return str(template_dir)

    def _get_static_dir(self) -> str:
        """Get the static files directory path."""
        current_dir = Path(__file__).parent
        static_dir = current_dir / "static"
        static_dir.mkdir(exist_ok=True)
        return str(static_dir)

    def _register_routes(self):
        """Register all route handlers for the unified interface."""

        # Main application route
        @self.app.route("/")
        def index():
            return render_template("unified_interface.html")

        # Legacy dashboard route (for backward compatibility)
        @self.app.route("/dashboard")
        def dashboard():
            return render_template("dashboard.html")

        # Connection test route (for debugging)
        @self.app.route("/test")
        def test_connection():
            return render_template("test_connection.html")

        # Project management routes
        @self.app.route("/api/projects", methods=["GET"])
        def get_projects():
            return jsonify(self.project_manager.list_projects())

        @self.app.route("/api/projects", methods=["POST"])
        def create_project():
            data = request.get_json()
            project = self.project_manager.create_project(data)
            return jsonify(project.to_dict())

        @self.app.route("/api/projects/<project_id>", methods=["GET"])
        def get_project(project_id: str):
            project = self.project_manager.get_project(project_id)
            return jsonify(project.to_dict() if project else None)

        # Template management routes
        @self.app.route("/api/templates", methods=["GET"])
        def get_templates():
            return jsonify(self.template_manager.list_templates())

        @self.app.route("/api/templates/<template_id>", methods=["GET"])
        def get_template(template_id: str):
            template = self.template_manager.get_template(template_id)
            return jsonify(template if template else None)

        # Configuration validation routes
        @self.app.route("/api/validate/city", methods=["POST"])
        def validate_city_config():
            config_data = request.get_json()
            config = SimulationConfiguration(config_data)
            validation_result = config.validate()
            return jsonify(validation_result)

        @self.app.route("/api/validate/population", methods=["POST"])
        def validate_population_config():
            config_data = request.get_json()
            config = SimulationConfiguration(config_data)
            validation_result = config.validate()
            return jsonify(validation_result)

        @self.app.route("/api/validate/simulation", methods=["POST"])
        def validate_simulation_config():
            config_data = request.get_json()
            config = SimulationConfiguration(config_data)
            validation_result = config.validate()
            return jsonify(validation_result)

        @self.app.route("/api/validate/review", methods=["POST"])
        def validate_review_config():
            # Review step validation - comprehensive check of entire configuration
            config_data = request.get_json()
            config = SimulationConfiguration(config_data)
            validation_result = config.validate()
            return jsonify(validation_result)

        # Simulation control routes
        @self.app.route("/api/simulation/start", methods=["POST"])
        def start_simulation():
            config = request.get_json()
            simulation_id = self.simulation_manager.start_simulation(config)
            return jsonify({"simulation_id": simulation_id, "status": "started"})

        @self.app.route("/api/simulation/<sim_id>/status", methods=["GET"])
        def get_simulation_status(sim_id: str):
            status = self.simulation_manager.get_status(sim_id)
            return jsonify(status)

        # Data export routes
        @self.app.route("/api/export/<sim_id>/<export_type>", methods=["POST"])
        def export_simulation_data(sim_id: str, export_type: str):
            options = request.get_json() or {}
            export_path = self.simulation_manager.export_data(
                sim_id, export_type, options
            )
            return jsonify({"export_path": str(export_path), "status": "complete"})

        # Shutdown route used by the desktop launcher to cleanly stop the server
        @self.app.route("/shutdown", methods=["POST"])
        def shutdown_server():  # pragma: no cover - tested via desktop launcher
            self.stop_server()
            return "Server shutting down"

    def _register_socket_handlers(self):
        """Setup SocketIO event handlers."""

        @self.socketio.on("connect")
        def handle_connect():
            print(f"Client connected to unified interface: {request.sid}")
            emit("connected", {"status": "connected"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            print(f"Client disconnected from unified interface: {request.sid}")

        @self.socketio.on("validation_request")
        def handle_validation_request(data):
            """Handle real-time validation requests."""
            try:
                config = SimulationConfiguration(data)
                result = config.validate()
                emit("validation_result", result)
            except Exception as e:
                emit("validation_error", {"message": str(e)})

    def start_server(self, threaded: bool = True):
        """Start the unified interface server."""
        print(f"Starting Simulacra Unified Interface on http://localhost:{self.port}")

        if threaded:
            server_thread = threading.Thread(
                target=lambda: self.socketio.run(
                    self.app,
                    host="0.0.0.0",
                    port=self.port,
                    debug=self.debug,
                    use_reloader=False,
                ),
                daemon=True,
            )
            server_thread.start()
            print(f"Unified interface running at http://localhost:{self.port}")
        else:
            self.socketio.run(
                self.app, host="0.0.0.0", port=self.port, debug=self.debug
            )

    def integrate_visualization_server(self, visualization_server: VisualizationServer):
        """Integrate with existing visualization server for backward compatibility."""
        self.visualization_server = visualization_server

        # Add routes to proxy to visualization server if needed
        @self.app.route("/api/city-layout")
        def get_city_layout():
            if self.visualization_server:
                return self.visualization_server.app.view_functions["get_city_layout"]()
            return jsonify({"error": "Visualization server not available"})

        @self.app.route("/api/realtime-data")
        def get_realtime_data():
            if self.visualization_server:
                return self.visualization_server.app.view_functions[
                    "get_realtime_data"
                ]()
            return jsonify({"error": "Visualization server not available"})

    def stop_server(self) -> None:
        """Stop the running SocketIO server if possible."""
        try:
            if getattr(self.socketio, "server", None) and getattr(
                self.socketio, "wsgi_server", None
            ):
                self.socketio.stop()
        except RuntimeError:
            pass
