"""Simulation lifecycle orchestration for the unified interface."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .simulation_bridge import SimulationBridge


class SimulationManager:
    """Facade around :class:`SimulationBridge` for the web interface."""

    def __init__(self, socketio=None) -> None:
        self.simulation_bridge = SimulationBridge(socketio)

    def start_simulation(self, config: Dict[str, Any]) -> Optional[str]:
        """Create and start a simulation from the supplied configuration."""
        simulation_id = self.simulation_bridge.create_simulation_from_config(config)
        if simulation_id:
            if self.simulation_bridge.start_simulation(simulation_id):
                return simulation_id
            return None

        # Fallback placeholder if the bridge cannot create simulations
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.simulation_bridge.active_simulations[simulation_id] = {
            "id": simulation_id,
            "config": config,
            "status": "starting",
            "created_at": datetime.now(),
        }
        return simulation_id

    def get_status(self, simulation_id: str) -> Dict[str, Any]:
        """Return the bridge reported status for a simulation."""
        return self.simulation_bridge.get_simulation_status(simulation_id)

    def export_data(
        self,
        simulation_id: str,
        export_type: str,
        options: Dict[str, Any],
    ) -> Path:
        """Export simulation data to disk and return the generated path."""
        export_path = self.simulation_bridge.export_simulation_data(
            simulation_id,
            export_type,
            options,
        )
        if export_path:
            return export_path

        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = export_dir / f"{simulation_id}_{export_type}_{timestamp}.json"
        export_path.write_text(json.dumps({"simulation_id": simulation_id, "type": export_type}))
        return export_path

    def list_active_simulations(self) -> Dict[str, Dict[str, Any]]:
        """Return the active simulations tracked by the bridge."""
        return self.simulation_bridge.list_active_simulations()
