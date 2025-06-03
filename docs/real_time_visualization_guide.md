# Real-time Visualization System Guide

## Phase 8.1: Real-time Visualization Implementation

This guide covers the implementation of the real-time visualization system for Simulacra, allowing you to monitor the simulation as it runs with an interactive web-based dashboard.

## Overview

The real-time visualization system provides:

- **City Map Visualization**: Interactive map showing agent locations and building placement
- **Agent State Indicators**: Real-time visual representation of agent states (stress, wealth, employment)
- **Building Occupancy Tracking**: Live monitoring of building capacity utilization
- **Heat Maps**: Spatial visualization of stress, addiction, and wealth distributions
- **Population Metrics**: Real-time aggregate statistics
- **Interactive Controls**: Pause, resume, and parameter adjustment

## Architecture

The system consists of three main components:

1. **DataStreamer**: Collects and formats real-time data from the simulation
2. **VisualizationServer**: Flask-based web server with WebSocket support for real-time updates
3. **RealtimeDashboard**: Main integration class that coordinates everything

## Quick Start

### Installation

First, install the required dependencies:

```bash
pip install flask flask-socketio python-socketio gevent gevent-websocket
```

### Basic Usage

```python
from src.simulation.simulation import Simulation
from src.visualization.real_time_dashboard import RealtimeDashboard

# Create your simulation
simulation = create_your_simulation()  # Your simulation setup

# Create and start dashboard
dashboard = RealtimeDashboard(
    simulation=simulation,
    port=5000,
    update_interval=1.0
)

# Start dashboard (non-blocking)
dashboard.start(threaded=True)

# Run simulation
simulation.run()

# Stop dashboard when done
dashboard.stop()
```

### Running the Demo

```bash
# Full web dashboard demo
python demo_realtime_visualization.py

# Headless demo (no web interface)
python demo_realtime_visualization.py --headless
```

## Dashboard Features

### City Map

The interactive city map displays:

- **Districts**: Color-coded by wealth level
- **Buildings**: Different shapes for different building types
- **Agents**: Moving dots representing agents, colored by stress level
- **Heat Maps**: Overlaid spatial data visualization

### Controls

- **View Toggles**: Show/hide agents, buildings, heat maps
- **Simulation Controls**: Pause, resume, stop simulation
- **Update Interval**: Adjust real-time update frequency
- **Manual Refresh**: Force immediate data update

### Metrics Display

Real-time metrics include:

- **Population Statistics**: Total agents, employment rate, housing rate
- **Health Indicators**: Average stress, mood, addiction levels
- **Economic Indicators**: Wealth distribution, inequality measures
- **Building Occupancy**: Capacity utilization by building type

## Technical Details

### Data Flow

1. **Simulation** → agents, environment state
2. **MetricsCollector** → aggregate statistics
3. **DataStreamer** → formatted JSON data
4. **VisualizationServer** → WebSocket updates
5. **Web Dashboard** → interactive visualization

### Performance Considerations

- **Update Interval**: Balance between responsiveness and performance (default: 1 second)
- **Agent Limit**: Tested with up to 100 agents; may need optimization for larger populations
- **Data Caching**: Static city layout is cached to improve performance
- **WebSocket Efficiency**: Only changed data is transmitted when possible

### Customization

#### Visual Appearance

Agent appearance can be customized by modifying the `DataStreamer` class:

```python
def _get_agent_color(self, agent: Agent) -> str:
    """Customize agent colors based on any attribute."""
    if agent.internal_state.stress > 0.8:
        return '#FF0000'  # Red for high stress
    elif agent.employment is not None:
        return '#00FF00'  # Green for employed
    else:
        return '#FFA500'  # Orange for unemployed

def _get_agent_size(self, agent: Agent) -> float:
    """Customize agent size based on wealth."""
    wealth = agent.internal_state.wealth
    return max(3, min(12, 3 + (wealth / 1000) * 9))
```

#### Adding New Metrics

To add new real-time metrics:

1. Extend the `MetricsCollector` class
2. Update `DataStreamer.get_realtime_data()`
3. Modify the dashboard template to display new data

#### Heat Map Types

Currently supports:
- **Stress**: Agent stress levels by location
- **Addiction**: Addiction levels by location  
- **Wealth**: Average wealth by location

To add new heat maps, modify `DataStreamer._get_heat_map_data()`.

## API Reference

### RealtimeDashboard

Main dashboard class for real-time visualization.

#### Constructor

```python
RealtimeDashboard(
    simulation: Simulation,
    metrics_collector: Optional[MetricsCollector] = None,
    port: int = 5000,
    update_interval: float = 1.0,
    debug: bool = False
)
```

#### Methods

- `start(threaded: bool = True)`: Start the dashboard
- `stop()`: Stop the dashboard
- `get_status()`: Get current dashboard status
- `set_update_interval(interval: float)`: Change update frequency
- `export_current_data(filepath: str = None)`: Export data to JSON
- `get_dashboard_url()`: Get dashboard URL

### DataStreamer

Handles real-time data collection and formatting.

#### Key Methods

- `get_city_layout_data()`: Static city structure
- `get_realtime_data()`: Current simulation state
- `_get_agent_data()`: Agent locations and states
- `_get_building_occupancy_data()`: Building utilization
- `_get_heat_map_data()`: Spatial heat map data

### VisualizationServer

Flask-based web server with WebSocket support.

#### Endpoints

- `GET /`: Main dashboard page
- `GET /api/city-layout`: Static city data
- `GET /api/realtime-data`: Current simulation data
- `POST /api/simulation-control`: Control simulation

#### WebSocket Events

- `connect`: Client connects to dashboard
- `realtime_update`: Live data updates
- `request_update`: Manual update request
- `change_update_interval`: Adjust update frequency

## Troubleshooting

### Common Issues

1. **Flask not installed**: Install with `pip install flask flask-socketio`

2. **Port already in use**: Change port in dashboard constructor:
   ```python
   dashboard = RealtimeDashboard(simulation, port=5001)
   ```

3. **Dashboard not updating**: Check that simulation is running and update interval is reasonable

4. **Performance issues**: 
   - Reduce update frequency
   - Limit number of agents
   - Disable heat maps if not needed

5. **Browser compatibility**: Dashboard works best with modern browsers supporting WebSocket

### Debug Mode

Enable debug mode for detailed logging:

```python
dashboard = RealtimeDashboard(simulation, debug=True)
```

### Logging

The system uses Python's logging module. To see detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements for future phases:

- **3D Visualization**: Three-dimensional city representation
- **Agent Interaction Networks**: Social connection visualization
- **Historical Playback**: Replay past simulation states
- **Advanced Analytics**: Pattern recognition and clustering
- **Mobile Responsive**: Tablet and mobile device support
- **Multi-simulation**: Compare multiple simulations side-by-side

## Integration with Existing Analytics

The real-time visualization system integrates seamlessly with existing Phase 7 analytics:

- **CSV Export**: Dashboard can export data in same format as existing analytics
- **Metrics Compatibility**: Uses same `MetricsCollector` class
- **History Tracking**: Maintains compatibility with existing history system

## Examples

### Basic Integration

```python
# Standard simulation setup
from src.simulation.simulation import Simulation, SimulationConfig
from src.environment.city import create_demo_city
from src.analytics.metrics import MetricsCollector
from src.visualization.real_time_dashboard import RealtimeDashboard

# Create simulation
config = SimulationConfig(max_months=12, max_agents=50)
city = create_demo_city()
simulation = Simulation(city, config)

# Add agents...
simulation.add_agents(create_agents())

# Create dashboard
metrics_collector = MetricsCollector()
dashboard = RealtimeDashboard(simulation, metrics_collector)

# Start visualization
with dashboard:
    simulation.run()
    # Dashboard automatically starts and stops
```

### Custom Metrics Dashboard

```python
# Extended metrics collection
class CustomMetricsCollector(MetricsCollector):
    def collect_custom_metrics(self, agents):
        # Add your custom metrics here
        pass

dashboard = RealtimeDashboard(
    simulation=simulation,
    metrics_collector=CustomMetricsCollector(),
    update_interval=0.5  # Fast updates
)
```

This real-time visualization system provides a powerful tool for understanding simulation dynamics as they unfold, enabling better analysis and debugging of agent behaviors and population trends. 