"""
Example visualization script for Simulacra data.
Shows how to create various plots from the exported CSV data.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from datetime import datetime


def load_simulation_data(output_dir: Path) -> dict:
    """
    Load all CSV data from a simulation run.

    Args:
        output_dir: Directory containing simulation output

    Returns:
        Dictionary of DataFrames
    """
    csv_dir = output_dir / "csv"

    data = {}

    # Load agent metrics timeseries
    agent_metrics_path = csv_dir / "agent_metrics_timeseries.csv"
    if agent_metrics_path.exists():
        data['agent_metrics'] = pd.read_csv(agent_metrics_path)
        data['agent_metrics']['timestamp'] = pd.to_datetime(data['agent_metrics']['timestamp'])

    # Load population metrics
    pop_metrics_path = csv_dir / "population_metrics_timeseries.csv"
    if pop_metrics_path.exists():
        data['population_metrics'] = pd.read_csv(pop_metrics_path)
        data['population_metrics']['timestamp'] = pd.to_datetime(data['population_metrics']['timestamp'])

    # Load agent trajectories
    trajectories_path = csv_dir / "agent_trajectories.csv"
    if trajectories_path.exists():
        data['trajectories'] = pd.read_csv(trajectories_path)
        data['trajectories']['timestamp'] = pd.to_datetime(data['trajectories']['timestamp'])

    # Load life events
    events_path = csv_dir / "life_events.csv"
    if events_path.exists():
        data['life_events'] = pd.read_csv(events_path)
        data['life_events']['timestamp'] = pd.to_datetime(data['life_events']['timestamp'])

    return data


def plot_population_overview(data: dict, save_dir: Path) -> None:
    """Create overview plots of population-level metrics."""
    pop_metrics = data.get('population_metrics')
    if pop_metrics is None or pop_metrics.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Population Overview', fontsize=16)

    # Employment and homelessness rates
    ax = axes[0, 0]
    ax.plot(pop_metrics['timestamp'], pop_metrics['employment_rate'] * 100,
            label='Employment Rate', marker='o')
    ax.plot(pop_metrics['timestamp'], pop_metrics['homelessness_rate'] * 100,
            label='Homelessness Rate', marker='s')
    ax.set_ylabel('Rate (%)')
    ax.set_xlabel('Time')
    ax.set_title('Employment and Housing')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Wealth distribution
    ax = axes[0, 1]
    ax.plot(pop_metrics['timestamp'], pop_metrics['mean_wealth'],
            label='Mean', marker='o')
    ax.plot(pop_metrics['timestamp'], pop_metrics['median_wealth'],
            label='Median', marker='s')
    ax.fill_between(pop_metrics['timestamp'],
                    pop_metrics['mean_wealth'] - pop_metrics['wealth_std'],
                    pop_metrics['mean_wealth'] + pop_metrics['wealth_std'],
                    alpha=0.3, label='±1 Std Dev')
    ax.set_ylabel('Wealth ($)')
    ax.set_xlabel('Time')
    ax.set_title('Wealth Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Addiction and stress
    ax = axes[1, 0]
    ax.plot(pop_metrics['timestamp'], pop_metrics['addiction_rate'] * 100,
            label='Addiction Rate', marker='o', color='red')
    ax.plot(pop_metrics['timestamp'], pop_metrics['high_stress_rate'] * 100,
            label='High Stress Rate', marker='s', color='orange')
    ax.set_ylabel('Rate (%)')
    ax.set_xlabel('Time')
    ax.set_title('Health Indicators')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Inequality
    ax = axes[1, 1]
    ax.plot(pop_metrics['timestamp'], pop_metrics['wealth_gini_coefficient'],
            marker='o', color='purple')
    ax.set_ylabel('Gini Coefficient')
    ax.set_xlabel('Time')
    ax.set_title('Wealth Inequality')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_dir / 'population_overview.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_agent_trajectories(data: dict, save_dir: Path, n_agents: int = 10) -> None:
    """Plot individual agent trajectories."""
    trajectories = data.get('trajectories')
    if trajectories is None or trajectories.empty:
        return

    # Get unique agents
    agents = trajectories['agent_id'].unique()[:n_agents]

    # Create subplots for different attributes
    attributes = ['wealth', 'stress', 'mood', 'alcohol_addiction_level']
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Agent Trajectories (First {n_agents} Agents)', fontsize=16)
    axes = axes.flatten()

    for idx, attr in enumerate(attributes):
        ax = axes[idx]
        attr_data = trajectories[trajectories['attribute'] == attr]

        for agent_id in agents:
            agent_data = attr_data[attr_data['agent_id'] == agent_id]
            if not agent_data.empty:
                ax.plot(agent_data['timestamp'], agent_data['value'],
                       alpha=0.7, linewidth=1, label=f'Agent {agent_id[:8]}')

        ax.set_ylabel(attr.replace('_', ' ').title())
        ax.set_xlabel('Time')
        ax.set_title(f'{attr.replace("_", " ").title()} Over Time')
        ax.grid(True, alpha=0.3)

        # Only show legend for first plot to avoid clutter
        if idx == 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(save_dir / 'agent_trajectories.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_life_events_timeline(data: dict, save_dir: Path) -> None:
    """Create timeline visualization of life events."""
    events = data.get('life_events')
    if events is None or events.empty:
        return

    # Count events by type
    event_counts = events['event_type'].value_counts()

    # Create bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Event counts
    ax1.bar(range(len(event_counts)), event_counts.values)
    ax1.set_xticks(range(len(event_counts)))
    ax1.set_xticklabels(event_counts.index, rotation=45, ha='right')
    ax1.set_ylabel('Count')
    ax1.set_title('Life Events by Type')
    ax1.grid(True, alpha=0.3, axis='y')

    # Events over time
    events['month'] = events['timestamp'].dt.to_period('M')
    events_by_month = events.groupby(['month', 'event_type']).size().unstack(fill_value=0)

    # Stack plot
    ax2.stackplot(events_by_month.index.astype(str),
                  events_by_month.T.values,
                  labels=events_by_month.columns,
                  alpha=0.8)
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Event Count')
    ax2.set_title('Life Events Over Time')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_dir / 'life_events_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_behavioral_patterns(data: dict, save_dir: Path) -> None:
    """Visualize behavioral patterns in the population."""
    agent_metrics = data.get('agent_metrics')
    if agent_metrics is None or agent_metrics.empty:
        return

    # Get latest metrics for each agent
    latest_metrics = agent_metrics.sort_values('timestamp').groupby('agent_id').last()

    # Create scatter plot matrix
    features = ['wealth', 'stress_level', 'alcohol_addiction_level', 'gambling_habit_strength']
    feature_data = latest_metrics[features]

    # Create pair plot
    fig, axes = plt.subplots(len(features), len(features), figsize=(15, 15))
    fig.suptitle('Agent Behavioral Patterns', fontsize=16)

    for i, feat1 in enumerate(features):
        for j, feat2 in enumerate(features):
            ax = axes[i, j]

            if i == j:
                # Diagonal: histogram
                ax.hist(feature_data[feat1], bins=20, alpha=0.7)
                ax.set_ylabel('Count')
            else:
                # Off-diagonal: scatter plot
                scatter = ax.scatter(feature_data[feat2], feature_data[feat1],
                                   c=latest_metrics['employed'].astype(int),
                                   cmap='RdYlGn', alpha=0.6)

            if i == len(features) - 1:
                ax.set_xlabel(feat2.replace('_', ' ').title())
            if j == 0:
                ax.set_ylabel(feat1.replace('_', ' ').title())

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=axes, label='Employed (0=No, 1=Yes)')

    plt.tight_layout()
    plt.savefig(save_dir / 'behavioral_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_action_distribution(data: dict, save_dir: Path) -> None:
    """Plot distribution of actions taken by agents."""
    pop_metrics = data.get('population_metrics')
    if pop_metrics is None or pop_metrics.empty:
        return

    # Get action frequency columns
    action_cols = [col for col in pop_metrics.columns if col.startswith('action_freq_')]
    if not action_cols:
        return

    # Get latest distribution
    latest = pop_metrics.iloc[-1]
    action_freqs = {col.replace('action_freq_', ''): latest[col]
                   for col in action_cols if latest[col] > 0}

    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))

    wedges, texts, autotexts = ax.pie(action_freqs.values(),
                                      labels=action_freqs.keys(),
                                      autopct='%1.1f%%',
                                      startangle=90)

    ax.set_title('Distribution of Agent Actions', fontsize=16)

    plt.savefig(save_dir / 'action_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_summary_dashboard(data: dict, save_dir: Path) -> None:
    """Create a summary dashboard with key metrics."""
    pop_metrics = data.get('population_metrics')
    agent_metrics = data.get('agent_metrics')
    events = data.get('life_events')

    if pop_metrics is None or pop_metrics.empty:
        return

    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

    # Title
    fig.suptitle('Simulacra Simulation Dashboard', fontsize=20)

    # Key metrics over time
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(pop_metrics['timestamp'], pop_metrics['employment_rate'] * 100,
            label='Employment %', linewidth=2)
    ax1.plot(pop_metrics['timestamp'], pop_metrics['addiction_rate'] * 100,
            label='Addiction %', linewidth=2)
    ax1.plot(pop_metrics['timestamp'], pop_metrics['homelessness_rate'] * 100,
            label='Homeless %', linewidth=2)
    ax1.set_ylabel('Rate (%)')
    ax1.set_title('Key Population Metrics')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Wealth inequality
    ax2 = fig.add_subplot(gs[0, 2:])
    ax2.plot(pop_metrics['timestamp'], pop_metrics['wealth_gini_coefficient'],
            color='purple', linewidth=2)
    ax2.set_ylabel('Gini Coefficient')
    ax2.set_title('Wealth Inequality Over Time')
    ax2.grid(True, alpha=0.3)

    # Final wealth distribution
    if agent_metrics is not None and not agent_metrics.empty:
        latest_metrics = agent_metrics.sort_values('timestamp').groupby('agent_id').last()

        ax3 = fig.add_subplot(gs[1, :2])
        ax3.hist(latest_metrics['wealth'], bins=30, alpha=0.7, color='green')
        ax3.axvline(latest_metrics['wealth'].mean(), color='red',
                   linestyle='--', label=f'Mean: ${latest_metrics["wealth"].mean():.0f}')
        ax3.axvline(latest_metrics['wealth'].median(), color='blue',
                   linestyle='--', label=f'Median: ${latest_metrics["wealth"].median():.0f}')
        ax3.set_xlabel('Wealth ($)')
        ax3.set_ylabel('Number of Agents')
        ax3.set_title('Final Wealth Distribution')
        ax3.legend()

        # Addiction vs Wealth scatter
        ax4 = fig.add_subplot(gs[1, 2:])
        scatter = ax4.scatter(latest_metrics['wealth'],
                            latest_metrics['alcohol_addiction_level'],
                            c=latest_metrics['employed'].astype(int),
                            cmap='RdYlGn', alpha=0.6)
        ax4.set_xlabel('Wealth ($)')
        ax4.set_ylabel('Addiction Level')
        ax4.set_title('Wealth vs Addiction (Color = Employment)')
        plt.colorbar(scatter, ax=ax4, label='Employed')

    # Life events summary
    if events is not None and not events.empty:
        ax5 = fig.add_subplot(gs[2, :])
        event_counts = events['event_type'].value_counts().head(10)
        ax5.barh(event_counts.index, event_counts.values)
        ax5.set_xlabel('Count')
        ax5.set_title('Top 10 Life Events')
        ax5.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(save_dir / 'simulation_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Main function to create all visualizations."""
    # Find the most recent simulation output
    output_base = Path("simulation_output")
    if not output_base.exists():
        print("No simulation output found. Please run demo_analytics_system.py first.")
        return

    # Get most recent output directory
    output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir()])
    if not output_dirs:
        print("No simulation output directories found.")
        return

    output_dir = output_dirs[-1]  # Most recent
    print(f"Loading data from: {output_dir}")

    # Load data
    data = load_simulation_data(output_dir)

    # Create visualizations directory
    viz_dir = output_dir / "visualizations"
    viz_dir.mkdir(exist_ok=True)

    # Create all visualizations
    print("Creating population overview...")
    plot_population_overview(data, viz_dir)

    print("Creating agent trajectories...")
    plot_agent_trajectories(data, viz_dir)

    print("Creating life events timeline...")
    plot_life_events_timeline(data, viz_dir)

    print("Creating behavioral patterns...")
    plot_behavioral_patterns(data, viz_dir)

    print("Creating action distribution...")
    plot_action_distribution(data, viz_dir)

    print("Creating summary dashboard...")
    create_summary_dashboard(data, viz_dir)

    print(f"\nAll visualizations saved to: {viz_dir}")
    print("\nVisualization files created:")
    for file in viz_dir.glob("*.png"):
        print(f"  - {file.name}")


if __name__ == "__main__":
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")

    main()
