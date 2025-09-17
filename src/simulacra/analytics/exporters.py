"""
Export capabilities for simulation data.
Implements Phase 7.3 of the roadmap.
"""
import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
import numpy as np
from collections import defaultdict

from .metrics import MetricsCollector
from .history import (
    HistoryTracker, EventType
)
from simulacra.utils.types import AgentID


class DataExporter(ABC):
    """Abstract base class for data exporters."""

    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize exporter with output directory.

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, data: Any, filename: str, **kwargs) -> Path:
        """
        Export data to file.

        Args:
            data: Data to export
            filename: Name of output file
            **kwargs: Additional export options

        Returns:
            Path to exported file
        """
        pass


class CSVExporter(DataExporter):
    """Export simulation data to CSV files."""

    def export(self, data: Any, filename: str, **kwargs) -> Path:
        """Export data to CSV file."""
        filepath = self.output_dir / f"{filename}.csv"

        if isinstance(data, list) and data and hasattr(data[0], 'to_dict'):
            # Export list of dataclass objects
            self._export_dataclass_list(data, filepath)
        elif isinstance(data, dict):
            # Export dictionary data
            self._export_dict(data, filepath)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

        return filepath

    def _export_dataclass_list(self, data: List[Any], filepath: Path) -> None:
        """Export list of dataclass objects to CSV."""
        if not data:
            return

        # Convert to list of dictionaries
        rows = [item.to_dict() for item in data]

        # Flatten nested dictionaries
        flattened_rows = []
        for row in rows:
            flattened = self._flatten_dict(row)
            flattened_rows.append(flattened)

        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if flattened_rows:
                writer = csv.DictWriter(f, fieldnames=flattened_rows[0].keys())
                writer.writeheader()
                writer.writerows(flattened_rows)

    def _export_dict(self, data: Dict, filepath: Path) -> None:
        """Export dictionary to CSV."""
        rows = []
        for key, value in data.items():
            if isinstance(value, dict):
                row = {'key': key, **self._flatten_dict(value)}
            else:
                row = {'key': key, 'value': value}
            rows.append(row)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))  # Convert lists to JSON strings
            else:
                items.append((new_key, v))
        return dict(items)

    def export_agent_metrics_timeseries(
        self,
        metrics_collector: MetricsCollector,
        agent_ids: Optional[List[AgentID]] = None
    ) -> Path:
        """
        Export agent metrics as time series data.

        Args:
            metrics_collector: Metrics collector with agent data
            agent_ids: Specific agents to export (None = all)

        Returns:
            Path to exported file
        """
        filepath = self.output_dir / "agent_metrics_timeseries.csv"

        rows = []
        for agent_id, metrics in metrics_collector.agent_metrics.items():
            if agent_ids is None or agent_id in agent_ids:
                row = metrics.to_dict()
                row['agent_id'] = agent_id
                rows.append(row)

        # Sort by timestamp and agent_id
        rows.sort(key=lambda x: (x['timestamp'], x['agent_id']))

        # Write to CSV
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)

        return filepath

    def export_population_metrics_timeseries(
        self,
        metrics_collector: MetricsCollector
    ) -> Path:
        """Export population metrics time series."""
        filepath = self.output_dir / "population_metrics_timeseries.csv"

        rows = []
        for metrics in metrics_collector.population_metrics_history:
            row = metrics.to_dict()
            # Flatten action distribution
            for action_type, freq in row.get('action_distribution', {}).items():
                row[f'action_freq_{action_type}'] = freq
            del row['action_distribution']
            rows.append(row)

        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)

        return filepath

    def export_agent_trajectories(
        self,
        history_tracker: HistoryTracker,
        attributes: List[str],
        agent_ids: Optional[List[AgentID]] = None
    ) -> Path:
        """
        Export agent state trajectories.

        Args:
            history_tracker: History tracker with agent data
            attributes: List of attributes to export (e.g., ['wealth', 'stress'])
            agent_ids: Specific agents to export

        Returns:
            Path to exported file
        """
        filepath = self.output_dir / "agent_trajectories.csv"

        rows = []
        for attribute in attributes:
            trajectories = history_tracker.get_population_trajectories(attribute, agent_ids)

            for agent_id, trajectory in trajectories.items():
                for timestamp, value in trajectory:
                    rows.append({
                        'agent_id': agent_id,
                        'timestamp': timestamp,
                        'attribute': attribute,
                        'value': value
                    })

        if rows:
            df = pd.DataFrame(rows)
            df.sort_values(['agent_id', 'attribute', 'timestamp'], inplace=True)
            df.to_csv(filepath, index=False)

        return filepath

    def export_life_events(
        self,
        history_tracker: HistoryTracker,
        event_types: Optional[List[EventType]] = None
    ) -> Path:
        """Export life events from all agents."""
        filepath = self.output_dir / "life_events.csv"

        rows = []
        for agent_id, history in history_tracker.agent_histories.items():
            for event in history.life_events:
                if event_types is None or event.event_type in event_types:
                    row = event.to_dict()
                    row['agent_id'] = agent_id
                    rows.append(row)

        if rows:
            df = pd.DataFrame(rows)
            df.sort_values(['timestamp', 'agent_id'], inplace=True)
            df.to_csv(filepath, index=False)

        return filepath


class JSONExporter(DataExporter):
    """Export simulation data to JSON files."""

    def export(self, data: Any, filename: str, **kwargs) -> Path:
        """Export data to JSON file."""
        filepath = self.output_dir / f"{filename}.json"

        # Convert data to serializable format
        serializable_data = self._make_serializable(data)

        # Write to JSON with formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                serializable_data,
                f,
                indent=kwargs.get('indent', 2),
                default=str  # Convert non-serializable objects to strings
            )

        return filepath

    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        else:
            return obj

    def export_full_simulation_state(
        self,
        metrics_collector: MetricsCollector,
        history_tracker: HistoryTracker,
        simulation_metadata: Dict[str, Any]
    ) -> Path:
        """
        Export complete simulation state.

        Args:
            metrics_collector: Metrics collector
            history_tracker: History tracker
            simulation_metadata: Additional simulation info

        Returns:
            Path to exported file
        """
        state = {
            'metadata': simulation_metadata,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'latest_population': metrics_collector.get_latest_population_metrics(),
                'behavioral_patterns': metrics_collector.behavioral_patterns,
                'economic_indicators': metrics_collector.economic_indicators_history
            },
            'agent_count': len(history_tracker.agent_histories),
            'total_months': history_tracker.current_month
        }

        return self.export(state, "simulation_state")

    def export_agent_histories(
        self,
        history_tracker: HistoryTracker,
        agent_ids: Optional[List[AgentID]] = None,
        include_full_history: bool = False
    ) -> Path:
        """
        Export agent histories.

        Args:
            history_tracker: History tracker
            agent_ids: Specific agents to export
            include_full_history: Include complete action/event history

        Returns:
            Path to exported file
        """
        histories = {}
        for agent_id, history in history_tracker.agent_histories.items():
            if agent_ids is None or agent_id in agent_ids:
                if include_full_history:
                    histories[agent_id] = history.to_dict()
                else:
                    # Export summary only
                    histories[agent_id] = {
                        'creation_time': history.creation_time,
                        'personality_traits': history.personality_traits,
                        'total_actions': history.total_actions,
                        'total_months_survived': history.total_months_survived,
                        'peak_wealth': history.peak_wealth,
                        'lowest_wealth': history.lowest_wealth,
                        'life_events_count': len(history.life_events),
                        'final_state': history.state_snapshots[-1] if history.state_snapshots else None
                    }

        return self.export(histories, "agent_histories")


class StatisticalReporter:
    """Generate statistical reports from simulation data."""

    def __init__(self, output_dir: Union[str, Path]):
        """Initialize reporter with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary_report(
        self,
        metrics_collector: MetricsCollector,
        history_tracker: HistoryTracker,
        simulation_metadata: Dict[str, Any]
    ) -> Path:
        """
        Generate comprehensive statistical summary report.

        Args:
            metrics_collector: Metrics collector
            history_tracker: History tracker
            simulation_metadata: Simulation information

        Returns:
            Path to report file
        """
        filepath = self.output_dir / "statistical_summary.txt"

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("SIMULACRA STATISTICAL SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")

            # Metadata
            f.write("SIMULATION METADATA\n")
            f.write("-" * 30 + "\n")
            for key, value in simulation_metadata.items():
                f.write(f"{key}: {value}\n")
            f.write(f"Report generated: {datetime.now()}\n\n")

            # Population statistics
            latest_pop_metrics = metrics_collector.get_latest_population_metrics()
            if latest_pop_metrics:
                f.write("POPULATION STATISTICS\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total agents: {latest_pop_metrics.total_agents}\n")
                f.write(f"Employment rate: {latest_pop_metrics.employment_rate:.1%}\n")
                f.write(f"Homelessness rate: {latest_pop_metrics.homelessness_rate:.1%}\n")
                f.write(f"Addiction rate: {latest_pop_metrics.addiction_rate:.1%}\n")
                f.write(f"Mean wealth: ${latest_pop_metrics.mean_wealth:,.2f}\n")
                f.write(f"Median wealth: ${latest_pop_metrics.median_wealth:,.2f}\n")
                f.write(f"Wealth inequality (Gini): {latest_pop_metrics.wealth_gini_coefficient:.3f}\n")
                f.write(f"Mean stress level: {latest_pop_metrics.mean_stress:.2f}\n")
                f.write(f"High stress rate: {latest_pop_metrics.high_stress_rate:.1%}\n\n")

            # Behavioral patterns
            if metrics_collector.behavioral_patterns:
                f.write("BEHAVIORAL PATTERNS\n")
                f.write("-" * 30 + "\n")
                for pattern in metrics_collector.behavioral_patterns:
                    f.write(f"\n{pattern.pattern_type.upper()}\n")
                    f.write(f"  Agents affected: {pattern.agent_count}\n")
                    if pattern.avg_duration > 0:
                        f.write(f"  Average duration: {pattern.avg_duration:.1f} months\n")
                    for key, value in pattern.characteristics.items():
                        if isinstance(value, float):
                            f.write(f"  {key}: {value:.3f}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                f.write("\n")

            # Action distribution
            if latest_pop_metrics and latest_pop_metrics.action_distribution:
                f.write("ACTION DISTRIBUTION\n")
                f.write("-" * 30 + "\n")
                sorted_actions = sorted(
                    latest_pop_metrics.action_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for action_type, frequency in sorted_actions:
                    f.write(f"{str(action_type).split('.')[-1]}: {frequency:.1%}\n")
                f.write("\n")

            # Life events summary
            f.write("LIFE EVENTS SUMMARY\n")
            f.write("-" * 30 + "\n")
            event_counts = defaultdict(int)
            for history in history_tracker.agent_histories.values():
                for event in history.life_events:
                    event_counts[event.event_type] += 1

            for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{event_type.value}: {count}\n")
            f.write("\n")

            # Agent outcomes
            f.write("AGENT OUTCOMES\n")
            f.write("-" * 30 + "\n")

            wealth_changes = []
            addiction_progressions = []

            for agent_id, history in history_tracker.agent_histories.items():
                if len(history.state_snapshots) >= 2:
                    initial = history.state_snapshots[0]
                    final = history.state_snapshots[-1]

                    wealth_change = final.wealth - initial.wealth
                    wealth_changes.append(wealth_change)

                    addiction_change = final.alcohol_addiction_level - initial.alcohol_addiction_level
                    addiction_progressions.append(addiction_change)

            if wealth_changes:
                f.write(f"Average wealth change: ${np.mean(wealth_changes):,.2f}\n")
                f.write(f"Median wealth change: ${np.median(wealth_changes):,.2f}\n")
                f.write(f"Agents with wealth increase: {sum(1 for w in wealth_changes if w > 0)} "
                       f"({sum(1 for w in wealth_changes if w > 0) / len(wealth_changes):.1%})\n")

            if addiction_progressions:
                f.write(f"\nAgents developing addiction: {sum(1 for a in addiction_progressions if a > 0.3)} "
                       f"({sum(1 for a in addiction_progressions if a > 0.3) / len(addiction_progressions):.1%})\n")

            # Economic indicators over time
            if metrics_collector.economic_indicators_history:
                f.write("\nECONOMIC TRENDS\n")
                f.write("-" * 30 + "\n")

                initial_econ = metrics_collector.economic_indicators_history[0]
                final_econ = metrics_collector.economic_indicators_history[-1]

                f.write(f"Unemployment rate change: "
                       f"{initial_econ.unemployment_rate:.1%} → {final_econ.unemployment_rate:.1%}\n")
                f.write(f"Average rent change: "
                       f"${initial_econ.average_rent:,.2f} → ${final_econ.average_rent:,.2f}\n")
                f.write(f"Income inequality change: "
                       f"{initial_econ.income_inequality:.3f} → {final_econ.income_inequality:.3f}\n")

        return filepath

    def generate_agent_report(
        self,
        agent_id: AgentID,
        metrics_collector: MetricsCollector,
        history_tracker: HistoryTracker
    ) -> Path:
        """
        Generate detailed report for a specific agent.

        Args:
            agent_id: Agent to report on
            metrics_collector: Metrics collector
            history_tracker: History tracker

        Returns:
            Path to report file
        """
        filepath = self.output_dir / f"agent_report_{agent_id}.txt"

        history = history_tracker.get_agent_history(agent_id)
        if not history:
            return filepath

        metrics = metrics_collector.get_agent_metrics(agent_id)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"AGENT REPORT: {agent_id}\n")
            f.write("=" * 50 + "\n\n")

            # Basic info
            f.write("AGENT CHARACTERISTICS\n")
            f.write("-" * 30 + "\n")
            traits = history.personality_traits
            f.write(f"Impulsivity: {traits.baseline_impulsivity:.2f}\n")
            f.write(f"Risk preference (α/β/λ): {traits.risk_preference_alpha:.2f}/"
                   f"{traits.risk_preference_beta:.2f}/{traits.risk_preference_lambda:.2f}\n")
            f.write(f"Cognitive type: {traits.cognitive_type:.2f}\n")
            f.write(f"Addiction vulnerability: {traits.addiction_vulnerability:.2f}\n")
            f.write(f"Initial wealth: ${history.initial_wealth:,.2f}\n\n")

            # Current state
            if metrics:
                f.write("CURRENT STATE\n")
                f.write("-" * 30 + "\n")
                f.write(f"Wealth: ${metrics.wealth:,.2f}\n")
                f.write(f"Employed: {'Yes' if metrics.employed else 'No'}\n")
                f.write(f"Housed: {'Yes' if metrics.housed else 'No'}\n")
                f.write(f"Stress level: {metrics.stress_level:.2f}\n")
                f.write(f"Mood: {metrics.mood_level:+.2f}\n")
                f.write(f"Addiction level: {metrics.alcohol_addiction_level:.2f}\n\n")

            # Life events
            f.write("SIGNIFICANT LIFE EVENTS\n")
            f.write("-" * 30 + "\n")
            for event in history.life_events:
                f.write(f"{event.timestamp}: {event.description}\n")
            if not history.life_events:
                f.write("No significant events recorded\n")
            f.write("\n")

            # Action summary
            f.write("ACTION SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total actions: {history.total_actions}\n")
            f.write(f"Months survived: {history.total_months_survived}\n")

            if agent_id in metrics_collector.agent_action_counts:
                action_counts = metrics_collector.agent_action_counts[agent_id]
                f.write("\nAction frequencies:\n")
                for action, count in action_counts.most_common():
                    f.write(f"  {str(action).split('.')[-1]}: {count}\n")

        return filepath
