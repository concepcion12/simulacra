"""
Real-time dashboard for Simulacra simulation visualization.
Main class that integrates data streaming and visualization server.
"""
from typing import Optional, Dict, Any
import threading
import time
from pathlib import Path

from src.simulation.simulation import Simulation
from src.analytics.metrics import MetricsCollector
from .data_streamer import DataStreamer
from .visualization_server import VisualizationServer


class RealtimeDashboard:
    """
    Main real-time dashboard for Simulacra simulation.
    
    Integrates:
    - Data streaming from simulation
    - Web-based visualization server
    - Real-time updates via WebSocket
    - Interactive controls
    """
    
    def __init__(
        self,
        simulation: Simulation,
        metrics_collector: Optional[MetricsCollector] = None,
        port: int = 5000,
        update_interval: float = 1.0,
        debug: bool = False
    ):
        """
        Initialize real-time dashboard.
        
        Args:
            simulation: The simulation instance to visualize
            metrics_collector: Metrics collector (creates new if None)
            port: Port for web server
            update_interval: Update interval in seconds
            debug: Enable debug mode
        """
        self.simulation = simulation
        
        # Create metrics collector if not provided
        if metrics_collector is None:
            self.metrics_collector = MetricsCollector()
        else:
            self.metrics_collector = metrics_collector
        
        # Initialize components
        self.data_streamer = DataStreamer(simulation, self.metrics_collector)
        self.visualization_server = VisualizationServer(
            self.data_streamer, 
            port=port, 
            debug=debug
        )
        
        # Dashboard state
        self.is_running = False
        self.update_interval = update_interval
        self._metrics_thread: Optional[threading.Thread] = None
        
        # Setup simulation event handlers for metrics collection
        self._setup_simulation_hooks()
    
    def _setup_simulation_hooks(self) -> None:
        """Setup hooks into simulation for automatic metrics collection."""
        # Add event handler for metrics collection
        from src.simulation.time_manager import TimeEvent
        
        def collect_metrics_handler(event_type, agents, time_manager):
            """Collect metrics when month ends."""
            if event_type == TimeEvent.MONTH_END:
                self.metrics_collector.collect_population_metrics(agents, time_manager.current_time)
        
        self.simulation.add_event_handler(TimeEvent.MONTH_END, collect_metrics_handler)
    
    def start(self, threaded: bool = True) -> None:
        """
        Start the real-time dashboard.
        
        Args:
            threaded: Run in separate thread (non-blocking)
        """
        if self.is_running:
            print("Dashboard is already running")
            return
        
        print("Starting Simulacra Real-time Dashboard...")
        
        self.is_running = True
        
        # Start metrics collection thread
        self._metrics_thread = threading.Thread(
            target=self._metrics_collection_loop, 
            daemon=True
        )
        self._metrics_thread.start()
        
        # Start visualization server
        self.visualization_server.start_server(threaded=threaded)
        
        if threaded:
            print(f"Dashboard running at http://localhost:{self.visualization_server.port}")
            print("Dashboard is running in background. Call stop() to shutdown.")
        
    def stop(self) -> None:
        """Stop the dashboard."""
        if not self.is_running:
            return
        
        print("Stopping real-time dashboard...")
        
        self.is_running = False
        
        # Stop visualization server
        self.visualization_server.stop_server()
        
        # Wait for metrics thread to finish
        if self._metrics_thread and self._metrics_thread.is_alive():
            self._metrics_thread.join(timeout=2.0)
        
        print("Dashboard stopped")
    
    def _metrics_collection_loop(self) -> None:
        """Background thread for continuous metrics collection."""
        while self.is_running:
            try:
                # Collect metrics for all agents
                current_time = self.simulation.time_manager.current_time
                
                # Collect individual agent metrics
                for agent in self.simulation.agents:
                    self.metrics_collector.collect_agent_metrics(agent, current_time)
                
                # Collect population metrics periodically (less frequent)
                if int(time.time()) % 5 == 0:  # Every 5 seconds
                    self.metrics_collector.collect_population_metrics(
                        self.simulation.agents, 
                        current_time
                    )
                
            except Exception as e:
                print(f"Error in metrics collection: {e}")
            
            time.sleep(self.update_interval)
    
    def get_dashboard_url(self) -> str:
        """Get the dashboard URL."""
        return f"http://localhost:{self.visualization_server.port}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current dashboard status."""
        return {
            'is_running': self.is_running,
            'server_port': self.visualization_server.port,
            'update_interval': self.update_interval,
            'simulation_running': self.simulation.is_running,
            'total_agents': len(self.simulation.agents),
            'months_completed': self.simulation.months_completed,
            'dashboard_url': self.get_dashboard_url()
        }
    
    def set_update_interval(self, interval: float) -> None:
        """
        Set the update interval for real-time updates.
        
        Args:
            interval: Update interval in seconds (0.1 - 10.0)
        """
        self.update_interval = max(0.1, min(10.0, interval))
        self.visualization_server.update_interval = self.update_interval
    
    def export_current_data(self, filepath: Optional[str] = None) -> str:
        """
        Export current simulation data to file.
        
        Args:
            filepath: Output file path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        import json
        from datetime import datetime
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"simulacra_dashboard_export_{timestamp}.json"
        
        # Get all current data
        data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'dashboard_version': '1.0',
                'simulation_state': self.simulation.get_simulation_state()
            },
            'city_layout': self.data_streamer.get_city_layout_data(),
            'realtime_data': self.data_streamer.get_realtime_data(),
            'population_metrics': [
                metrics.to_dict() 
                for metrics in self.metrics_collector.population_metrics_history
            ],
            'agent_metrics': {
                agent_id: metrics.to_dict()
                for agent_id, metrics in self.metrics_collector.agent_metrics.items()
            }
        }
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Dashboard data exported to: {filepath}")
        return filepath
    
    def __enter__(self):
        """Context manager entry."""
        self.start(threaded=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def __repr__(self) -> str:
        return (
            f"RealtimeDashboard(running={self.is_running}, "
            f"port={self.visualization_server.port}, "
            f"agents={len(self.simulation.agents)})"
        ) 
