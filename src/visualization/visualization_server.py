"""
Visualization server for real-time simulation dashboard.
Uses Flask with SocketIO for real-time updates.
"""
import os
import json
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
except ImportError:
    Flask = None
    SocketIO = None
    print("Warning: Flask and flask-socketio not installed. Install with: pip install flask flask-socketio")

from .data_streamer import DataStreamer


class VisualizationServer:
    """
    Real-time visualization server for Simulacra simulation.
    
    Provides a web-based dashboard with:
    - City map with agent locations
    - Real-time metrics display
    - Heat maps for stress, addiction, wealth
    - Building occupancy indicators
    """
    
    def __init__(self, data_streamer: DataStreamer, port: int = 5000, debug: bool = False):
        """
        Initialize visualization server.
        
        Args:
            data_streamer: Data streamer instance
            port: Port to run server on
            debug: Enable Flask debug mode
        """
        if Flask is None:
            raise ImportError("Flask is required for visualization server. Install with: pip install flask flask-socketio")
        
        self.data_streamer = data_streamer
        self.port = port
        self.debug = debug
        
        # Flask app setup
        self.app = Flask(__name__, template_folder=self._get_template_dir())
        self.app.config['SECRET_KEY'] = 'simulacra_viz_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Server state
        self.is_running = False
        self.update_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0  # seconds
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
    
    def _get_template_dir(self) -> str:
        """Get the templates directory path."""
        current_dir = Path(__file__).parent
        template_dir = current_dir / "templates"
        template_dir.mkdir(exist_ok=True)
        return str(template_dir)
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/city-layout')
        def get_city_layout():
            """Get static city layout data."""
            try:
                layout_data = self.data_streamer.get_city_layout_data()
                return jsonify(layout_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/realtime-data')
        def get_realtime_data():
            """Get current real-time simulation data."""
            try:
                data = self.data_streamer.get_realtime_data()
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/simulation-control', methods=['POST'])
        def simulation_control():
            """Control simulation (pause/resume/stop)."""
            try:
                action = request.json.get('action')
                simulation = self.data_streamer.simulation
                
                if action == 'pause':
                    simulation.pause()
                    return jsonify({'status': 'paused'})
                elif action == 'resume':
                    simulation.resume()
                    return jsonify({'status': 'running'})
                elif action == 'stop':
                    simulation.stop()
                    return jsonify({'status': 'stopped'})
                else:
                    return jsonify({'error': 'Invalid action'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_socket_handlers(self) -> None:
        """Setup SocketIO event handlers."""
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            print(f"Client connected: {request.sid}")
            # Send initial data
            try:
                layout_data = self.data_streamer.get_city_layout_data()
                realtime_data = self.data_streamer.get_realtime_data()
                
                emit('city_layout', layout_data)
                emit('realtime_update', realtime_data)
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            print(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle manual update request from client."""
            try:
                data = self.data_streamer.get_realtime_data()
                emit('realtime_update', data)
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('change_update_interval')
        def handle_interval_change(data):
            """Handle update interval change request."""
            try:
                new_interval = float(data.get('interval', 1.0))
                self.update_interval = max(0.1, min(10.0, new_interval))  # Clamp between 0.1-10 seconds
                emit('interval_changed', {'interval': self.update_interval})
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def start_server(self, threaded: bool = True) -> None:
        """
        Start the visualization server.
        
        Args:
            threaded: Run server in a separate thread
        """
        if self.is_running:
            print("Server is already running")
            return
        
        self.is_running = True
        
        # Start real-time update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        print(f"Starting visualization server on http://localhost:{self.port}")
        
        if threaded:
            # Run server in a separate thread
            server_thread = threading.Thread(
                target=lambda: self.socketio.run(
                    self.app, 
                    host='0.0.0.0', 
                    port=self.port, 
                    debug=self.debug,
                    use_reloader=False
                ),
                daemon=True
            )
            server_thread.start()
            print(f"Visualization server running at http://localhost:{self.port}")
        else:
            # Run server in main thread (blocking)
            self.socketio.run(
                self.app, 
                host='0.0.0.0', 
                port=self.port, 
                debug=self.debug
            )
    
    def stop_server(self) -> None:
        """Stop the visualization server."""
        self.is_running = False
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
        
        print("Visualization server stopped")
    
    def _update_loop(self) -> None:
        """Background thread that sends real-time updates to connected clients."""
        while self.is_running:
            try:
                data = self.data_streamer.get_realtime_data()
                self.socketio.emit('realtime_update', data)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                self.socketio.emit('error', {'message': str(e)})
            
            time.sleep(self.update_interval)
    
    def __enter__(self):
        """Context manager entry."""
        self.start_server(threaded=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server() 