# Simulacra: Agent-Based Simulation

Simulacra is a sophisticated agent-based simulation system that models complex social dynamics, behavioral economics, and addiction patterns in urban environments. The system implements behavioral economics principles, dual-process cognition, and environmental cue systems to create realistic agent behaviors.

## 🌟 Features

### Core Simulation System
- **Behavioral Economics**: Agents with realistic decision-making based on utility theory
- **Dual-Process Cognition**: System 1 (fast, automatic) and System 2 (slow, deliberate) thinking
- **Environmental Cues**: Spatial proximity affects agent behavior and decision-making
- **Addiction Modeling**: Sophisticated substance dependency and habit formation
- **Economic System**: Dynamic job market, housing, and economic conditions

### Environment & Spatial System
- **Multi-District Cities**: Districts with varying wealth levels and characteristics
- **Building Types**: Residential, commercial, industrial buildings with specific functions
- **Spatial Mechanics**: Distance-based interactions and movement costs
- **Dynamic Economy**: Market conditions affecting employment and housing

### Advanced Analytics
- **Real-time Metrics**: Comprehensive agent and population-level statistics
- **Historical Tracking**: Detailed life event and behavioral pattern recording
- **Data Export**: CSV and JSON export for external analysis
- **Behavioral Pattern Recognition**: Automatic identification of common agent behaviors

### Real-time Visualization
- **Interactive Dashboard**: Web-based real-time monitoring
- **City Map Visualization**: Live agent locations and building occupancy
- **Heat Maps**: Spatial visualization of stress, addiction, and wealth
- **Population Metrics**: Real-time aggregate statistics and trends

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Simulacra
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **For full visualization features (optional)**
```bash
pip install flask flask-socketio python-socketio gevent gevent-websocket
```

### Basic Usage

```python
from src.simulation.simulation import Simulation, SimulationConfig
from src.environment.city import City
from src.population.population_generator import QuickPopulationFactory

# Create a simulation
config = SimulationConfig(max_months=12, max_agents=100)
simulation = create_your_simulation(config)  # See examples below

# Run the simulation
simulation.run()
```

## 📋 Complete Setup Guide

### 1. Environment Setup

```python
from src.environment.city import City
from src.environment.district import District
from src.environment.plot import Plot
from src.environment.buildings.residential import ResidentialBuilding, HousingUnit
from src.environment.buildings.employer import Employer, JobOpening
from src.environment.buildings.liquor_store import LiquorStore
from src.environment.buildings.casino import Casino, GamblingGame

# Create districts
poor_district = District("poor", "Downtown", wealth_level=1, plots=[])
middle_district = District("middle", "Midtown", wealth_level=3, plots=[])
rich_district = District("rich", "Uptown", wealth_level=5, plots=[])

# Create buildings
shelter_plot = Plot("shelter_1", (10, 10), "poor", "residential")
shelter_units = [HousingUnit(f"unit_{i}", 50, 0.2) for i in range(10)]
shelter = ResidentialBuilding("shelter", shelter_plot, shelter_units, 0.2)

# Create city
city = City("Demo City", [poor_district, middle_district, rich_district])
```

### 2. Population Generation

```python
from src.population.population_generator import QuickPopulationFactory

# Quick generation methods
agents = QuickPopulationFactory.create_balanced_population(50)  # Realistic population
agents = QuickPopulationFactory.create_diverse_population(50)   # Maximum diversity
agents = QuickPopulationFactory.create_vulnerable_population(50) # Higher addiction risk
agents = QuickPopulationFactory.create_mixed_population(50, vulnerable_proportion=0.3)

# Custom generation with specific distributions
from src.population.distribution_config import DistributionConfig
from src.population.population_generator import PopulationGenerator

config = DistributionConfig.create_realistic_default()
generator = PopulationGenerator(config, seed=42)
agents = generator.generate_population(50)
```

### 3. Simulation Configuration

```python
from src.simulation.simulation import Simulation, SimulationConfig

config = SimulationConfig(
    max_months=24,          # Run for 2 years
    rounds_per_month=10,    # 10 action rounds per month
    max_agents=100,         # Maximum agent capacity
    enable_logging=True,    # Enable detailed logging
    log_level="INFO"        # Logging level
)

simulation = Simulation(city, config)
simulation.add_agents(agents)
```

## 🎮 Running Simulations

### Demo Scripts

#### 1. Real-time Visualization Demo
```bash
# Full web dashboard with interactive visualization
python demo_realtime_visualization.py

# Headless mode (no web interface required)
python demo_realtime_visualization.py --headless
```

#### 2. Analytics System Demo
```bash
python demo_analytics_system.py
```

#### 3. Population Generation Demo
```bash
python demo_population_generation.py
```

#### 4. Economic System Demo
```bash
python demo_economic_system.py
```

#### 5. Time Management Demo
```bash
python demo_time_management.py
```

### Custom Simulations

```python
# Basic simulation
simulation = Simulation(city, config)
simulation.add_agents(agents)
results = simulation.run()

# With analytics
from src.analytics.metrics import MetricsCollector
from src.analytics.history import HistoryTracker

metrics_collector = MetricsCollector()
history_tracker = HistoryTracker()

# Run simulation with data collection
for month in range(12):
    simulation.run_single_month()
    
    # Collect metrics
    pop_metrics = metrics_collector.collect_population_metrics(
        simulation.agents, 
        simulation.time_manager.current_time
    )
    
    print(f"Month {month}: Employment {pop_metrics.employment_rate:.1%}")
```

## 📊 Real-time Visualization

### Starting the Dashboard

```python
from src.visualization.real_time_dashboard import RealtimeDashboard

# Create and start dashboard
dashboard = RealtimeDashboard(
    simulation=simulation,
    port=5000,              # Web server port
    update_interval=1.0     # Update every second
)

# Start dashboard (non-blocking)
dashboard.start(threaded=True)

# Run simulation
simulation.run()

# Stop dashboard
dashboard.stop()
```

### Dashboard Features

- **City Map**: Interactive visualization of agents and buildings
- **Real-time Metrics**: Population statistics, employment, housing rates
- **Heat Maps**: Spatial visualization of stress, addiction, wealth
- **Controls**: Pause, resume, stop simulation
- **Data Export**: Download current state as JSON

Access the dashboard at: `http://localhost:5000`

### Dashboard Controls

- **Agent View**: Toggle agent visibility and coloring (stress, wealth, employment)
- **Building View**: Show building occupancy and capacity
- **Heat Maps**: Overlay spatial data (stress, addiction, wealth levels)
- **Update Interval**: Adjust real-time update frequency (0.1-10 seconds)
- **Simulation Controls**: Pause, resume, or stop the running simulation

## 📈 Analytics & Data Collection

### Metrics Collection

```python
from src.analytics.metrics import MetricsCollector

collector = MetricsCollector(poverty_line=800.0)

# Collect agent-level metrics
for agent in agents:
    metrics = collector.collect_agent_metrics(agent, datetime.now())
    print(f"Agent {agent.id}: Wealth ${metrics.wealth:.0f}, Stress {metrics.stress_level:.2f}")

# Collect population metrics
pop_metrics = collector.collect_population_metrics(agents, datetime.now())
print(f"Population: {pop_metrics.employment_rate:.1%} employed, {pop_metrics.addiction_rate:.1%} addicted")
```

### Historical Tracking

```python
from src.analytics.history import HistoryTracker

tracker = HistoryTracker()

# Register agents for tracking
for agent in agents:
    tracker.register_agent(agent, datetime.now())

# Record actions and life events automatically during simulation
# Access detailed histories
history = tracker.get_agent_history(agent.id)
wealth_trajectory = history.get_state_trajectory('wealth')
action_sequence = history.get_action_sequence()
```

### Data Export

```python
# Export analytics data
from src.analytics.data_exporter import DataExporter

exporter = DataExporter("simulation_output")

# Export all data types
exporter.export_agent_metrics(collector.agent_metrics.values())
exporter.export_population_timeseries(collector.population_metrics_history)
exporter.export_agent_trajectories(tracker.get_all_histories())
exporter.export_life_events(tracker.get_all_histories())

# Creates CSV files for analysis in external tools
```

## 🔧 Advanced Features

### Custom Agent Behaviors

```python
from src.agents.agent import Agent
from src.utils.types import PersonalityTraits

# Create agent with specific personality
personality = PersonalityTraits(
    baseline_impulsivity=0.3,
    risk_preference_alpha=0.8,
    addiction_vulnerability=0.2
)

agent = Agent(
    agent_id="custom_001",
    name="Custom Agent",
    personality=personality,
    initial_wealth=1000.0
)
```

### Custom Buildings and Environments

```python
# Create custom building types
class CustomBuilding(Building):
    def generate_cues(self, agent_location):
        # Custom cue generation logic
        return []
    
    def can_interact(self, agent):
        # Custom interaction rules
        return True

# Add to city
plot = Plot("custom_1", (50, 50), "district_1", "custom")
building = CustomBuilding("custom_building", plot)
```

### Economic Interventions

```python
# Modify economic conditions during simulation
simulation.city.global_economy.set_unemployment_rate(0.15)
simulation.city.global_economy.trigger_economic_shock(-0.2)

# Add new buildings during simulation
new_employer = Employer("new_job_center", plot, "Job Center", job_openings)
district.plots.append(plot)
```

### Behavioral Pattern Analysis

```python
# Identify behavioral patterns
patterns = collector.identify_behavioral_patterns(agents)

for pattern in patterns:
    print(f"Pattern: {pattern.pattern_type}")
    print(f"Agents affected: {pattern.agent_count}")
    print(f"Characteristics: {pattern.characteristics}")
```

## 📁 Output and Data Analysis

### File Structure

```
simulation_output/
├── csv/
│   ├── agent_metrics_timeseries.csv
│   ├── population_metrics_timeseries.csv
│   ├── agent_trajectories.csv
│   └── life_events.csv
├── json/
│   └── full_simulation_state.json
└── visualizations/
    ├── population_overview.png
    ├── agent_trajectories.png
    └── behavioral_patterns.png
```

### Analysis Scripts

```python
# Load and analyze exported data
import pandas as pd

# Load metrics data
agent_data = pd.read_csv("simulation_output/csv/agent_metrics_timeseries.csv")
population_data = pd.read_csv("simulation_output/csv/population_metrics_timeseries.csv")

# Analyze trends
employment_trend = population_data['employment_rate'].rolling(window=5).mean()
addiction_correlation = agent_data.groupby('agent_id')[['stress_level', 'alcohol_addiction_level']].corr()
```

### Visualization Creation

```python
# Generate static visualizations
python visualization_example.py

# Creates comprehensive charts and plots in simulation_output/visualizations/
```

## 🛠️ Configuration Options

### Simulation Parameters

```python
SimulationConfig(
    max_months=12,          # Simulation duration
    rounds_per_month=10,    # Action frequency
    max_agents=100,         # Population limit
    enable_logging=True,    # Debug information
    log_level="INFO"        # Detail level
)
```

### Economic Settings

```python
# Adjust economic parameters
economy = simulation.city.global_economy
economy.set_base_unemployment_rate(0.08)
economy.set_inflation_rate(0.03)
economy.set_housing_market_conditions(0.7)
```

### Agent Generation Settings

```python
# Configure population characteristics
config = DistributionConfig(
    initial_wealth=NormalDistribution(mean=1000, std=500),
    personality_traits={
        'addiction_vulnerability': BetaDistribution(alpha=2, beta=5),
        'baseline_impulsivity': UniformDistribution(min=0.1, max=0.9)
    }
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
```bash
# Ensure you're in the project root directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or use absolute imports
```

2. **Memory Issues with Large Populations**
```python
# Use history size limits
tracker = HistoryTracker(max_history_size=1000)
# Reduce snapshot frequency
history.snapshot_interval = 20
```

3. **Performance Optimization**
```python
# Reduce update frequency for large simulations
config.rounds_per_month = 5
dashboard.set_update_interval(2.0)
```

4. **Visualization Server Issues**
```bash
# Check if port is available
lsof -i :5000
# Use different port
dashboard = RealtimeDashboard(simulation, port=5001)
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug mode for dashboard
dashboard = RealtimeDashboard(simulation, debug=True)
```

## 📚 Documentation

- **Real-time Visualization Guide**: `docs/real_time_visualization_guide.md`
- **Development Roadmap**: `docs/next_steps_roadmap.md`
- **Population Generation Guide**: `POPULATION_GENERATION_GUIDE.md`

## 🤝 Contributing

1. Follow the modular architecture patterns
2. Add comprehensive tests for new features
3. Update documentation for new components
4. Use type hints and docstrings
5. Follow the existing code style

## 📄 License

Simulacra is released under the MIT License. See the `LICENSE` file for full
license text.

## 🆘 Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the demo scripts for usage examples
3. Examine the comprehensive test suite for implementation details
4. Check the docs/ directory for detailed guides

---

**Simulacra** - Advanced Agent-Based Social Simulation System
*Modeling complex social dynamics through behavioral economics and environmental psychology* 
