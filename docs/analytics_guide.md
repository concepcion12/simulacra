# Simulacra Analytics System Guide

## Overview

The Simulacra analytics system (Phase 7.1-7.3) provides comprehensive data collection, history tracking, and export capabilities for simulation data. This guide explains how to use the system to collect data and create visualizations for analysis.

## Components

### 7.1 Metrics System (`src/analytics/metrics.py`)

The metrics system tracks both agent-level and population-level statistics:

#### Agent Metrics
- **Financial**: wealth, income, expenses, poverty ratio
- **Employment**: employment status, duration, performance
- **Housing**: housing status, quality, evictions
- **Mental Health**: stress, mood, self-control
- **Addiction**: addiction level, consumption frequency, tolerance, withdrawal
- **Behavioral**: gambling frequency, habit strength, action diversity

#### Population Metrics
- **Economic**: mean/median wealth, Gini coefficient, poverty rate
- **Social**: employment rate, homelessness rate
- **Health**: mean stress/mood, addiction prevalence
- **Behavioral**: action distribution across population

#### Behavioral Patterns
The system identifies patterns like:
- Addiction spirals (high addiction + poverty + stress)
- Stable employment (long tenure + good performance)
- Recovery patterns
- Social isolation

### 7.2 History Tracking (`src/analytics/history.py`)

Comprehensive history tracking for each agent:

#### State Snapshots
- Periodic snapshots of complete agent state
- Configurable snapshot frequency (default: every 10 actions)
- Tracks all internal state variables over time

#### Action Records
- Every action taken with context
- Pre/post state changes
- Available alternatives at decision time
- Success/failure outcomes

#### Life Events
- Significant events (job loss, eviction, addiction onset)
- Automatic detection from state changes
- Event impacts on agent state

### 7.3 Export Capabilities (`src/analytics/exporters.py`)

Multiple export formats for different use cases:

#### CSV Export
- Time series data for statistical analysis
- Agent trajectories for individual tracking
- Population metrics over time
- Life events log

#### JSON Export
- Complete simulation state
- Agent histories (full or summary)
- Nested data structures preserved
- Metadata included

#### Statistical Reports
- Human-readable summary reports
- Population-level statistics
- Individual agent reports
- Behavioral pattern analysis

## Usage

### Basic Integration

```python
from src.analytics.metrics import MetricsCollector
from src.analytics.history import HistoryTracker
from src.analytics.exporters import CSVExporter, JSONExporter, StatisticalReporter

# Initialize components
metrics_collector = MetricsCollector(poverty_line=800.0)
history_tracker = HistoryTracker(max_history_size=1000)

# Register agents
for agent in simulation.agents:
    history_tracker.register_agent(agent, datetime.now())

# During simulation, record actions
metrics_collector.record_action(agent.id, action_type, success)
history_tracker.record_action(agent, action, outcome, timestamp, pre_state, available_actions)

# Collect metrics periodically
population_metrics = metrics_collector.collect_population_metrics(agents, timestamp)
```

### Running a Monitored Simulation

Use the provided demo script:

```bash
python demo_analytics_system.py
```

This will:
1. Create a simulation with 50 diverse agents
2. Run for 6 months with comprehensive data collection
3. Export all data to `simulation_output/[timestamp]/`
4. Generate statistical reports

### Creating Visualizations

After running a simulation:

```bash
python visualization_example.py
```

This creates:
- Population overview plots
- Individual agent trajectories
- Life events timeline
- Behavioral pattern analysis
- Action distribution charts
- Summary dashboard

## Output Structure

```
simulation_output/
└── YYYYMMDD_HHMMSS/
    ├── csv/
    │   ├── agent_metrics_timeseries.csv
    │   ├── population_metrics_timeseries.csv
    │   ├── agent_trajectories.csv
    │   └── life_events.csv
    ├── json/
    │   ├── simulation_state.json
    │   └── agent_histories.json
    ├── reports/
    │   ├── statistical_summary.txt
    │   └── agent_report_[id].txt
    └── visualizations/
        ├── population_overview.png
        ├── agent_trajectories.png
        ├── behavioral_patterns.png
        └── simulation_dashboard.png
```

## Data Analysis Workflow

### 1. Quick Overview
- Check `reports/statistical_summary.txt` for key findings
- View `visualizations/simulation_dashboard.png` for visual summary

### 2. Population Analysis
- Load `csv/population_metrics_timeseries.csv` in pandas
- Track trends in employment, homelessness, addiction
- Analyze wealth inequality evolution

### 3. Individual Analysis
- Load `csv/agent_trajectories.csv` for state evolution
- Use `json/agent_histories.json` for detailed histories
- Track individual outcomes and patterns

### 4. Event Analysis
- Load `csv/life_events.csv` for significant events
- Correlate events with state changes
- Identify common event sequences

### 5. Custom Analysis
```python
import pandas as pd

# Load data
pop_metrics = pd.read_csv('population_metrics_timeseries.csv')
agent_metrics = pd.read_csv('agent_metrics_timeseries.csv')

# Custom analysis
addiction_by_wealth = agent_metrics.groupby('wealth_quartile')['alcohol_addiction_level'].mean()
```

## Advanced Features

### Custom Metrics
Extend `MetricsCollector` to track additional metrics:

```python
class ExtendedMetricsCollector(MetricsCollector):
    def collect_custom_metrics(self, agent):
        # Add your custom metrics
        pass
```

### Event Detection
Add custom life event detection:

```python
def detect_custom_events(self, agent, pre_state, post_state):
    if pre_state.wealth > 10000 and post_state.wealth < 1000:
        self.record_life_event(
            agent.id,
            EventType.FINANCIAL_COLLAPSE,
            "Major financial loss",
            timestamp
        )
```

### Real-time Monitoring
Hook into simulation events for real-time data collection:

```python
simulation.add_event_handler(TimeEvent.MONTH_END, on_month_end)
simulation.add_event_handler(TimeEvent.ACTION_EXECUTED, on_action)
```

## Performance Considerations

- **Memory Usage**: History tracking stores all actions. Use `max_history_size` to limit.
- **Snapshot Frequency**: Adjust `snapshot_interval` based on needs
- **Export Size**: Full histories can be large. Use summary mode for overview.
- **Real-time Collection**: Collecting metrics every action impacts performance

## Next Steps

1. **Visualization Dashboard**: Build interactive web dashboard using exported data
2. **Statistical Analysis**: Use R or Python notebooks for deeper analysis
3. **Machine Learning**: Train models on agent behavior patterns
4. **Parameter Optimization**: Use data to tune simulation parameters
5. **Intervention Testing**: Measure impact of policy interventions

## Example Analysis Questions

The analytics system helps answer questions like:

- What percentage of agents fall into addiction?
- How does initial wealth affect long-term outcomes?
- What are common paths to homelessness?
- Which behavioral patterns lead to stability?
- How does stress correlate with addiction?
- What is the impact of job loss on agent trajectories?

## Troubleshooting

### No data exported
- Ensure simulation ran successfully
- Check that agents were registered with history tracker
- Verify event handlers were properly registered

### Missing metrics
- Some metrics require multiple time points (e.g., wealth change)
- Behavioral frequencies need action history
- Check that actions are being recorded

### Large file sizes
- Reduce `max_history_size` for history tracker
- Use summary export mode instead of full history
- Export specific agent subsets rather than all

### Visualization errors
- Ensure pandas and matplotlib are installed
- Check that CSV files have expected columns
- Verify timestamp parsing is working 