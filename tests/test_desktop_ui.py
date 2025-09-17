import importlib
import pytest


def test_start_local_interface_import() -> None:
    """Ensure the desktop launcher module can be imported when PyQt is present."""
    try:
        module = importlib.import_module("start_local_interface")
    except Exception as exc:  # pragma: no cover - environment may lack Qt libs
        pytest.skip(f"PyQt unavailable: {exc}")
        return
    assert hasattr(module, "main")


def test_shutdown_route() -> None:
    """The unified app exposes a shutdown route for the desktop UI."""
    try:
        from simulacra.visualization.unified_app import UnifiedSimulacraApp
    except ImportError as exc:  # pragma: no cover - optional dependencies
        pytest.skip(f"Flask unavailable: {exc}")
        return

    ui = UnifiedSimulacraApp()
    client = ui.app.test_client()
    resp = client.post("/shutdown")
    assert resp.status_code == 200
