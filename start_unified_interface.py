#!/usr/bin/env python3
"""
Startup script for the Simulacra Unified Interface
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from visualization.unified_app import UnifiedSimulacraApp
    
    def main():
        print("🏙️  Starting Simulacra Unified Interface...")
        print("=" * 50)
        
        # Create and configure the app
        app = UnifiedSimulacraApp(port=5000, debug=True)
        
        print(f"📡 Server starting on http://localhost:5000")
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
            # Start the server in blocking mode (not threaded)
            app.start_server(threaded=False)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            print("💭 Make sure you have the required dependencies installed:")
            print("   pip install flask flask-socketio")
            return 1
        
        return 0

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💭 Make sure you have the required dependencies installed:")
    print("   pip install flask flask-socketio")
    print("\n📁 Current working directory:", os.getcwd())
    print("🔍 Python path includes:", src_dir)
    sys.exit(1) 
