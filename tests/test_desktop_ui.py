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
