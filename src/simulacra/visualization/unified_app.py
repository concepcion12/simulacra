"""Unified Flask application for the Simulacra interface."""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

try:  # pragma: no cover - optional dependency wiring
    from flask import Flask, jsonify, render_template, request
    from flask_socketio import SocketIO, emit
except ImportError as exc:  # pragma: no cover - handled at runtime
    Flask = None  # type: ignore[assignment]
    SocketIO = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:  # pragma: no cover - executed when dependencies available
    _IMPORT_ERROR = None

from .visualization_server import VisualizationServer
from .configuration import SimulationConfiguration
from .project_management import ProjectManager, Project
from .template_library import TemplateManager
from .simulation_control import SimulationManager


class UnifiedSimulacraApp:
    """Compose the various managers into a Socket.IO enabled Flask app."""

    def __init__(self, port: int = 5000, debug: bool = False) -> None:
        if Flask is None or SocketIO is None:  # pragma: no cover - dependency guard
            raise ImportError(
                "Flask and flask-socketio are required. Install with: "
                "pip install flask flask-socketio"
            ) from _IMPORT_ERROR

        template_folder = self._ensure_directory("templates")
        static_folder = self._ensure_directory("static")

        self.app = Flask(
            __name__,
            template_folder=template_folder,
            static_folder=static_folder,
        )
        self.app.secret_key = os.getenv("SIMULACRA_SECRET_KEY", "simulacra_unified_secret_key")
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.debug = debug

        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()
        self.simulation_manager = SimulationManager(self.socketio)
        self.visualization_server: Optional[VisualizationServer] = None

        self._register_routes()
        self._register_socket_handlers()

    @staticmethod
    def _ensure_directory(name: str) -> str:
        """Ensure the template/static directories exist and return the path."""
        directory = Path(__file__).parent / name
        directory.mkdir(exist_ok=True)
        return str(directory)

    def _register_routes(self) -> None:
        """Register HTTP routes for the unified interface."""

        @self.app.route("/")
        def index() -> str:
            return render_template("unified_interface.html")

        @self.app.route("/dashboard")
        def dashboard() -> str:
            return render_template("dashboard.html")

        @self.app.route("/test")
        def test_connection() -> str:
            return render_template("test_connection.html")

        @self.app.route("/api/projects", methods=["GET"])
        def get_projects():
            projects: Iterable[Dict[str, Any]] = self.project_manager.list_projects()
            return jsonify(list(projects))

        @self.app.route("/api/projects", methods=["POST"])
        def create_project():
            data = request.get_json() or {}
            project = self.project_manager.create_project(data)
            return jsonify(project.to_dict())

        @self.app.route("/api/projects/<project_id>", methods=["GET"])
        def get_project(project_id: str):
            project = self.project_manager.get_project(project_id)
            return jsonify(project.to_dict() if project else None)

        @self.app.route("/api/templates", methods=["GET"])
        def get_templates():
            return jsonify(self.template_manager.list_templates())

        @self.app.route("/api/templates/<template_id>", methods=["GET"])
        def get_template(template_id: str):
            template = self.template_manager.get_template(template_id)
            return jsonify(template if template else None)

        @self.app.route("/api/validate/<section>", methods=["POST"])
        def validate_config_section(section: str):
            config_data = request.get_json() or {}
            config = SimulationConfiguration(**config_data)
            validation = config.validate()
            return jsonify(validation)

        @self.app.route("/api/simulation/start", methods=["POST"])
        def start_simulation():
            config = request.get_json() or {}
            simulation_id = self.simulation_manager.start_simulation(config)
            return jsonify({"simulation_id": simulation_id, "status": "started"})

        @self.app.route("/api/simulation/<sim_id>/status", methods=["GET"])
        def get_simulation_status(sim_id: str):
            status = self.simulation_manager.get_status(sim_id)
            return jsonify(status)

        @self.app.route("/api/export/<sim_id>/<export_type>", methods=["POST"])
        def export_simulation_data(sim_id: str, export_type: str):
            options = request.get_json() or {}
            export_path = self.simulation_manager.export_data(sim_id, export_type, options)
            return jsonify({"export_path": str(export_path), "status": "complete"})

        @self.app.route("/shutdown", methods=["POST"])
        def shutdown_server():  # pragma: no cover - integration tested via launcher
            self.stop_server()
            return "Server shutting down"

    def _register_socket_handlers(self) -> None:
        """Wire up Socket.IO event handlers for live validation."""

        @self.socketio.on("connect")
        def handle_connect():  # pragma: no cover - requires socket client
            emit("connected", {"status": "connected"})

        @self.socketio.on("validation_request")
        def handle_validation_request(data):  # pragma: no cover - requires socket client
            try:
                config = SimulationConfiguration(**data)
                emit("validation_result", config.validate())
            except Exception as exc:  # noqa: BLE001
                emit("validation_error", {"message": str(exc)})

    def start_server(self, threaded: bool = True) -> None:
        """Start the Socket.IO server."""
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
        else:
            self.socketio.run(self.app, host="0.0.0.0", port=self.port, debug=self.debug)

    def integrate_visualization_server(self, visualization_server: VisualizationServer) -> None:
        """Expose selected routes from the legacy visualization server."""
        self.visualization_server = visualization_server

        @self.app.route("/api/city-layout")
        def get_city_layout():
            if self.visualization_server:
                return self.visualization_server.app.view_functions["get_city_layout"]()
            return jsonify({"error": "Visualization server not available"})

        @self.app.route("/api/realtime-data")
        def get_realtime_data():
            if self.visualization_server:
                return self.visualization_server.app.view_functions["get_realtime_data"]()
            return jsonify({"error": "Visualization server not available"})

    def stop_server(self) -> None:
        """Attempt to stop the running Socket.IO server."""
        try:
            has_server = getattr(self.socketio, "server", None)
            has_wsgi_server = getattr(self.socketio, "wsgi_server", None)
            if has_server and has_wsgi_server:
                self.socketio.stop()
        except RuntimeError:
            pass


__all__ = [
    "UnifiedSimulacraApp",
    "ProjectManager",
    "Project",
    "TemplateManager",
    "SimulationConfiguration",
    "SimulationManager",
]
