#!/usr/bin/env python3
"""Launch Simulacra with an integrated desktop UI."""

from __future__ import annotations

import sys
from urllib.request import Request, urlopen

try:  # pragma: no cover - optional dependency wiring
    from PyQt6.QtCore import QUrl
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWidgets import QApplication
except ImportError as exc:  # pragma: no cover - handled at runtime
    _PYQT_IMPORT_ERROR = exc
else:  # pragma: no cover - executed when dependencies available
    _PYQT_IMPORT_ERROR = None

from simulacra.visualization.unified_app import UnifiedSimulacraApp


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
    if _PYQT_IMPORT_ERROR is not None:  # pragma: no cover - dependency guard
        raise ImportError(
            "PyQt6 is required for the desktop interface. Install with: pip install simulacra[desktop]"
        ) from _PYQT_IMPORT_ERROR

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
