#!/usr/bin/env python3
"""
Demo script for Simulacra Unified Interface - Phase 1 Implementation

This script demonstrates the core infrastructure implemented in Phase 1:
- Enhanced Flask application with unified workflow support
- Project and template management
- State management system
- SPA frontend framework

Run this script to launch the unified interface and explore the home section
with project management and template gallery functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path so we can import Simulacra modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.visualization.unified_app import UnifiedSimulacraApp
except ImportError as e:
    print(f"Error importing Simulacra modules: {e}")
    print("Make sure you're running this from the project root directory")
    print("and that all dependencies are installed.")
    sys.exit(1)


def main():
    """Main demo function."""
    print("=" * 60)
    print("🏙️  Simulacra Unified Interface - Phase 1 Demo")
    print("=" * 60)
    print()
    print("This demo showcases the Phase 1 implementation:")
    print("✅ Enhanced Flask application structure")
    print("✅ Project and template management")
    print("✅ State management system")
    print("✅ Modern SPA frontend with dark theme")
    print("✅ Real-time WebSocket communication")
    print()
    
    # Initialize the unified app
    print("Initializing Simulacra Unified Interface...")
    
    # Use port 5001 to avoid conflicts with any existing dashboard
    app = UnifiedSimulacraApp(port=5001, debug=True)
    
    print("✅ Core infrastructure initialized")
    print("✅ Project management system ready")
    print("✅ Template library loaded")
    print("✅ API endpoints configured")
    print()
    
    print("🚀 Starting unified interface server...")
    print()
    print("Open your browser and navigate to:")
    print("📱 http://localhost:5001")
    print()
    print("Features available in this demo:")
    print("• 🏠 Home section with project management")
    print("• 📋 Template gallery with 4 pre-configured templates")
    print("• 💾 Project save/load functionality")
    print("• 🔗 Real-time WebSocket connection status")
    print("• ⚙️  Setup wizard placeholder (Phase 2)")
    print("• 🔄 Legacy dashboard integration (/dashboard)")
    print()
    print("Templates included:")
    print("• 🏙️  Basic Urban Study (50 agents, 6 months)")
    print("• 🍺 Addiction Research (100 agents, 18 months)")
    print("• 💰 Economic Inequality (150 agents, 24 months)")
    print("• 🏛️  Policy Testing (200 agents, 12 months)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server (blocking)
        app.start_server(threaded=False)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Simulacra Unified Interface...")


if __name__ == "__main__":
    main()