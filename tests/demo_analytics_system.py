"""
Demonstration of the complete analytics system (Phase 7.1-7.3).
Shows how to collect metrics, track history, and export data for visualization.
"""
import logging
from datetime import datetime
from pathlib import Path

from src.environment.city import City
from src.environment.buildings import (
    ResidentialBuilding, LiquorStore, Casino, Employer, PublicSpace
)
from src.simulation.simulation import Simulation, SimulationConfig
from src.agents.agent import Agent
from src.analytics.metrics import MetricsCollector, EconomicIndicators
from src.analytics.history import HistoryTracker, EventType
from src.analytics.exporters import CSVExporter, JSONExporter, StatisticalReporter
from src.utils.types import PlotID, DistrictWealth


def create_monitored_simulation() -> tuple:
    """
    Create a simulation with comprehensive data collection.
    
    Returns:
        Tuple of (simulation, metrics_collector, history_tracker)
    """
    # Create city with diverse districts
    city = City()
    
    # Create districts
    downtown = city.add_district("Downtown", DistrictWealth.UPPER_CLASS, (50, 50), 20)
    midtown = city.add_district("Midtown", DistrictWealth.MIDDLE_CLASS, (50, 80), 20)
    eastside = city.add_district("Eastside", DistrictWealth.WORKING_CLASS, (80, 50), 20)
    southside = city.add_district("Southside", DistrictWealth.POOR, (50, 20), 20)
    
    # Add buildings to city
    # Downtown - expensive housing and employers
    city.add_building(
        ResidentialBuilding("Luxury Towers", capacity=20, quality=0.9, base_rent=2500),
        downtown.get_random_plot()
    )
    city.add_building(
        Employer("Tech Corp", job_capacity=15, avg_salary=4000, job_quality=0.8),
        downtown.get_random_plot()
    )
    city.add_building(
        Casino("High Stakes Casino", house_edge=0.05, min_bet=100),
        downtown.get_random_plot()
    )
    
    # Midtown - moderate housing and services
    city.add_building(
        ResidentialBuilding("Garden Apartments", capacity=30, quality=0.7, base_rent=1500),
        midtown.get_random_plot()
    )
    city.add_building(
        Employer("Office Complex", job_capacity=25, avg_salary=2500, job_quality=0.6),
        midtown.get_random_plot()
    )
    city.add_building(
        LiquorStore("Wines & Spirits", price_factor=1.2),
        midtown.get_random_plot()
    )
    
    # Eastside - working class area
    city.add_building(
        ResidentialBuilding("Workers Housing", capacity=40, quality=0.5, base_rent=800),
        eastside.get_random_plot()
    )
    city.add_building(
        Employer("Factory", job_capacity=30, avg_salary=1500, job_quality=0.4),
        eastside.get_random_plot()
    )
    city.add_building(
        LiquorStore("Corner Store", price_factor=1.0),
        eastside.get_random_plot()
    )
    city.add_building(
        Casino("Lucky's Gaming", house_edge=0.1, min_bet=10),
        eastside.get_random_plot()
    )
    
    # Southside - poor area
    city.add_building(
        ResidentialBuilding("Budget Motel", capacity=20, quality=0.3, base_rent=400),
        southside.get_random_plot()
    )
    city.add_building(
        PublicSpace("City Park", quality=0.3),
        southside.get_random_plot()
    )
    city.add_building(
        LiquorStore("Discount Liquor", price_factor=0.8),
        southside.get_random_plot()
    )
    
    # Configure simulation
    config = SimulationConfig(
        max_months=6,
        rounds_per_month=10,
        max_agents=50,
        enable_logging=True,
        log_level="INFO"
    )
    
    # Create simulation
    simulation = Simulation(city, config)
    
    # Create analytics components
    metrics_collector = MetricsCollector(poverty_line=800.0)
    history_tracker = HistoryTracker(max_history_size=1000)  # Keep last 1000 actions per agent
    
    return simulation, metrics_collector, history_tracker


def create_diverse_population(n_agents: int) -> list[Agent]:
    """Create a diverse population of agents."""
    agents = []
    
    # Create agents with different profiles
    profiles = ['vulnerable', 'impulsive', 'balanced', 'cautious']
    wealth_ranges = [(500, 1000), (1000, 2000), (2000, 5000), (5000, 10000)]
    
    for i in range(n_agents):
        profile = profiles[i % len(profiles)]
        wealth_range = wealth_ranges[i % len(wealth_ranges)]
        initial_wealth = wealth_range[0] + (wealth_range[1] - wealth_range[0]) * (i / n_agents)
        
        agent = Agent.create_with_profile(
            profile_type=profile,
            initial_wealth=initial_wealth
        )
        agents.append(agent)
    
    return agents


def integrate_analytics_with_simulation(
    simulation: Simulation,
    metrics_collector: MetricsCollector,
    history_tracker: HistoryTracker
) -> None:
    """
    Integrate analytics components with simulation events.
    
    Args:
        simulation: The simulation instance
        metrics_collector: Metrics collector
        history_tracker: History tracker
    """
    # Get current timestamp
    current_time = datetime.now()
    
    # Register existing agents with history tracker
    for agent in simulation.agents:
        history_tracker.register_agent(agent, current_time)
    
    # Hook into simulation events
    def on_action_executed(agent, action, outcome, context):
        """Called when an agent executes an action."""
        # Record in metrics collector
        metrics_collector.record_action(
            agent.id, 
            action.action_type,
            outcome.success
        )
        
        # Record in history tracker
        pre_state = agent.internal_state  # Would need to save this before action
        available_actions = context.available_actions if hasattr(context, 'available_actions') else []
        
        history_tracker.record_action(
            agent,
            action,
            outcome,
            current_time,
            pre_state,
            available_actions
        )
    
    def on_month_end(event_type, agents, time_manager):
        """Called at the end of each month."""
        nonlocal current_time
        current_time = datetime.now()
        
        # Collect population metrics
        metrics_collector.collect_population_metrics(agents, current_time)
        
        # Identify behavioral patterns
        patterns = metrics_collector.identify_behavioral_patterns(agents)
        
        # Advance month in history tracker
        history_tracker.advance_month()
        
        # Collect economic indicators
        unemployment_rate = sum(1 for a in agents if a.employment is None) / len(agents)
        employed_agents = [a for a in agents if a.employment is not None]
        avg_wage = sum(a.employment.salary for a in employed_agents) / len(employed_agents) if employed_agents else 0
        
        housed_agents = [a for a in agents if a.home is not None]
        avg_rent = sum(a.home.rent for a in housed_agents) / len(housed_agents) if housed_agents else 0
        
        wealths = [a.internal_state.wealth for a in agents]
        wealth_gini = metrics_collector._calculate_gini_coefficient(wealths)
        
        economic_indicators = EconomicIndicators(
            timestamp=current_time,
            unemployment_rate=unemployment_rate,
            inflation_rate=0.02,  # Placeholder
            housing_vacancy_rate=0.1,  # Placeholder
            average_rent=avg_rent,
            average_wage=avg_wage,
            income_inequality=wealth_gini,
            wealth_mobility=0.1,  # Placeholder
            liquor_store_revenue=0,  # Would need to track
            casino_revenue=0  # Would need to track
        )
        
        metrics_collector.economic_indicators_history.append(economic_indicators)
        
        # Log summary
        logging.info(f"Month {time_manager.current_time.month} analytics collected")
        logging.info(f"Behavioral patterns identified: {len(patterns)}")
        
    # Register event handlers
    from src.simulation.time_manager import TimeEvent
    simulation.add_event_handler(TimeEvent.MONTH_END, on_month_end)
    
    # Note: In a real implementation, you'd also hook into the action execution
    # This would require modifying the simulation to emit events or callbacks


def run_monitored_simulation():
    """Run a simulation with full analytics and export results."""
    print("Creating monitored simulation...")
    simulation, metrics_collector, history_tracker = create_monitored_simulation()
    
    print("Creating diverse population...")
    agents = create_diverse_population(50)
    simulation.add_agents(agents)
    
    print("Integrating analytics...")
    integrate_analytics_with_simulation(simulation, metrics_collector, history_tracker)
    
    print("\nRunning simulation...")
    monthly_stats = simulation.run()
    
    print("\nSimulation complete. Generating reports...")
    
    # Create output directory
    output_dir = Path("simulation_output") / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize exporters
    csv_exporter = CSVExporter(output_dir / "csv")
    json_exporter = JSONExporter(output_dir / "json")
    reporter = StatisticalReporter(output_dir / "reports")
    
    # Export data
    print("Exporting CSV data...")
    csv_exporter.export_agent_metrics_timeseries(metrics_collector)
    csv_exporter.export_population_metrics_timeseries(metrics_collector)
    csv_exporter.export_agent_trajectories(
        history_tracker,
        attributes=['wealth', 'stress', 'mood', 'alcohol_addiction_level'],
        agent_ids=[a.id for a in agents[:10]]  # First 10 agents for demo
    )
    csv_exporter.export_life_events(history_tracker)
    
    print("Exporting JSON data...")
    simulation_metadata = {
        'start_time': datetime.now().isoformat(),
        'config': simulation.config.__dict__,
        'city_districts': len(simulation.city.districts),
        'total_buildings': len(simulation.city.buildings),
        'initial_agents': len(agents)
    }
    
    json_exporter.export_full_simulation_state(
        metrics_collector,
        history_tracker,
        simulation_metadata
    )
    json_exporter.export_agent_histories(
        history_tracker,
        include_full_history=False  # Summary only for demo
    )
    
    print("Generating statistical reports...")
    reporter.generate_summary_report(
        metrics_collector,
        history_tracker,
        simulation_metadata
    )
    
    # Generate individual reports for a few agents
    sample_agents = agents[:3]
    for agent in sample_agents:
        reporter.generate_agent_report(
            agent.id,
            metrics_collector,
            history_tracker
        )
    
    print(f"\nAll data exported to: {output_dir}")
    
    # Print summary statistics
    latest_metrics = metrics_collector.get_latest_population_metrics()
    if latest_metrics:
        print("\nFinal Population Statistics:")
        print(f"  Total agents: {latest_metrics.total_agents}")
        print(f"  Employment rate: {latest_metrics.employment_rate:.1%}")
        print(f"  Homelessness rate: {latest_metrics.homelessness_rate:.1%}")
        print(f"  Addiction rate: {latest_metrics.addiction_rate:.1%}")
        print(f"  Mean wealth: ${latest_metrics.mean_wealth:,.2f}")
        print(f"  Wealth inequality (Gini): {latest_metrics.wealth_gini_coefficient:.3f}")
    
    # Show behavioral patterns
    if metrics_collector.behavioral_patterns:
        print(f"\nIdentified {len(metrics_collector.behavioral_patterns)} behavioral patterns")
        for pattern in metrics_collector.behavioral_patterns[:3]:  # Show first 3
            print(f"  - {pattern.pattern_type}: {pattern.agent_count} agents affected")
    
    return output_dir


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the monitored simulation
    output_dir = run_monitored_simulation()
    
    print("\n" + "=" * 50)
    print("SIMULATION WITH ANALYTICS COMPLETE")
    print("=" * 50)
    print(f"\nData saved to: {output_dir}")
    print("\nYou can now use this data for:")
    print("  - Visualization (CSV files can be loaded into plotting libraries)")
    print("  - Further analysis (JSON files contain complete state)")
    print("  - Reporting (Statistical summaries in reports folder)")
    print("\nNext steps:")
    print("  1. Use pandas/matplotlib to create visualizations from CSV data")
    print("  2. Load JSON data for detailed agent trajectory analysis")
    print("  3. Review statistical reports for insights") 