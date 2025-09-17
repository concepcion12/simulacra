#!/usr/bin/env python3
"""Startup script for the Simulacra Unified Interface."""

from __future__ import annotations

import sys

from simulacra.visualization.unified_app import UnifiedSimulacraApp


def main() -> int:
    """Launch the web-based unified interface."""
    print("🏙️  Starting Simulacra Unified Interface...")
    print("=" * 50)

    try:
        app = UnifiedSimulacraApp(port=5000, debug=True)
    except ImportError as exc:
        print(f"❌ Unable to start interface: {exc}")
        print("💭 Install optional dependencies with: pip install simulacra[visualization]")
        return 1

    print("📡 Server starting on http://localhost:5000")
    print("📋 Features available:")
    print("   • Setup Wizard - Complete simulation configuration")
    print("   • Project Management - Save/load configurations")
    print("   • Template Library - Pre-configured scenarios")
    print("   • Real-time Dashboard - Monitor running simulations")
    print("=" * 50)
    print("💡 Open your browser and navigate to: http://localhost:5000")
    print("🔧 The Setup Wizard will guide you through creating your first simulation!")
    print()

    try:
        app.start_server(threaded=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error starting server: {exc}")
        print("💭 Make sure you have the required dependencies installed:")
        print("   pip install simulacra[visualization]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
