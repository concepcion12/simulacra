# Simulacra: Basic Setup and Operation Guide

## Prerequisites
- Python 3.8 or later
- pip package manager

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Simulacra
   ```
2. Install core dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install visualization dependencies:
   ```bash
   pip install flask flask-socketio gevent gevent-websocket
   ```

## Quick Start
Run a basic simulation:
```bash
python demo_population_generation.py   # generate agents
python demo_time_management.py         # advance time
python demo_action_outcomes.py         # perform actions
python demo_economic_system.py         # simulate economy
``` 

## Feature Guide

### 1. Core Simulation System
- Configure and run:
  ```python
  from src.simulation.simulation import Simulation, SimulationConfig
  sim_config = SimulationConfig(max_months=12, rounds_per_month=10, max_agents=100)
  simulation = Simulation(city, sim_config)
  simulation.add_agents(agents)
  simulation.run()
  ```

### 2. Environment & Spatial System
- Create city, districts, and plots:
  ```python
  from src.environment.city import City
  from src.environment.district import District
  from src.environment.plot import Plot
  # define districts and plots
  city = City("Demo City", [district1, district2, ...])
  ```

### 3. Action Execution System
- Available actions: Work, Drink, Gamble, Rest, Housing/Job Search.
- Outcomes update agent state with stochastic elements.

### 4. Simulation Loop
- Full run:
  ```python
  simulation.run()
  ```
- Month-by-month:
  ```python
  for _ in range(sim_config.max_months):
      simulation.run_single_month()
  ```

### 5. Advanced Analytics
- Metrics collection:
  ```python
  from src.analytics.metrics import MetricsCollector
  collector = MetricsCollector()
  pop_metrics = collector.collect_population_metrics(simulation.agents, simulation.time_manager.current_time)
  ```
- History tracking:
  ```python
  from src.analytics.history import HistoryTracker
  tracker = HistoryTracker()
  ```

### 6. Real-time Visualization
- Launch dashboard:
  ```bash
  python demo_realtime_visualization.py [--headless]
  ```
- Access at: `http://localhost:5000`

### 7. Data Export
- Export to CSV/JSON:
  ```python
  from src.analytics.data_exporter import DataExporter
  exporter = DataExporter("output_dir")
  exporter.export_all()
  ```

### 8. Customization & Extensions
- Custom agents:
  ```python
  from src.agents.agent import Agent
  agent = Agent(agent_id="A1", personality=traits, initial_wealth=1000)
  ```
- Custom buildings & interventions:
  ```python
  # subclass Building or adjust economy:
  simulation.city.global_economy.set_unemployment_rate(0.1)
  ```

## Troubleshooting
- **Import Errors**: ensure `PYTHONPATH` includes project root.
- **Performance**: reduce `max_agents` or `rounds_per_month` in `SimulationConfig`.

## Additional Resources
- Full roadmap: `docs/next_steps_roadmap.md`
- Population guide: `POPULATION_GENERATION_GUIDE.md`
- Detailed examples: see `demo_*.py` scripts 