#!/usr/bin/env python3
"""
Launch Simulacra with an integrated desktop UI.

This script starts the unified Flask backend in a background thread
and embeds the web interface in a PyQt6 window so no external browser
is needed.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from urllib.request import Request, urlopen

# Ensure src directory is on path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from visualization.unified_app import UnifiedSimulacraApp


class SimulacraWindow(QWebEngineView):
    """Web view that shuts down the backend when closed."""

    def __init__(self, backend: UnifiedSimulacraApp) -> None:
        super().__init__()
        self.backend = backend

    def closeEvent(self, event) -> None:  # pragma: no cover - Qt GUI
        try:
            req = Request("http://localhost:5000/shutdown", method="POST")
            urlopen(req, timeout=2)
        except Exception as exc:  # noqa: BLE001
            print(f"Error shutting down server: {exc}")
        super().closeEvent(event)


def main() -> int:
    """Start the desktop interface."""
    # Start the backend server in a thread
    ui_app = UnifiedSimulacraApp(port=5000, debug=False)
    ui_app.start_server(threaded=True)

    qt_app = QApplication(sys.argv)
    view = SimulacraWindow(ui_app)
    view.setWindowTitle("Simulacra")
    view.resize(1200, 800)
    view.load(QUrl("http://localhost:5000"))
    view.show()

    return qt_app.exec()


if __name__ == "__main__":
    sys.exit(main())
