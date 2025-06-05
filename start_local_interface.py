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

# Ensure src directory is on path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from visualization.unified_app import UnifiedSimulacraApp


def main() -> int:
    """Start the desktop interface."""
    # Start the backend server in a thread
    ui_app = UnifiedSimulacraApp(port=5000, debug=False)
    ui_app.start_server(threaded=True)

    qt_app = QApplication(sys.argv)
    view = QWebEngineView()
    view.setWindowTitle("Simulacra")
    view.resize(1200, 800)
    view.load(QUrl("http://localhost:5000"))
    view.show()

    return qt_app.exec()


if __name__ == "__main__":
    sys.exit(main())
