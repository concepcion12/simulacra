"""
Demo script for Phase 8.1: Real-time Visualization
Shows how to use the real-time dashboard with a running simulation.
"""
import time
import threading
from pathlib import Path

# Import simulation components
from src.simulation.simulation import Simulation, SimulationConfig
from src.environment.city import City
from src.environment.district import District
from src.environment.plot import Plot
from src.environment.buildings.residential import ResidentialBuilding, HousingUnit
from src.environment.buildings.liquor_store import LiquorStore
from src.environment.buildings.casino import Casino, GamblingGame
from src.environment.buildings.employer import Employer, JobOpening
from src.analytics.metrics import MetricsCollector

# Import visualization components
from src.visualization.real_time_dashboard import RealtimeDashboard

# Import population generation
from src.population.population_generator import QuickPopulationFactory


def create_demo_city() -> City:
    """Create a demo city with districts and buildings."""
    print("Creating demo city...")
    
    # Create districts
    districts = []
    
    # Poor district
    poor_district = District(
        district_id="poor_district",
        name="Riverside",
        wealth_level=1,
        plots=[]
    )
    
    # Create plots and buildings for poor district
    poor_plots = []
    
    # Residential plot with shelter
    shelter_plot = Plot("plot_poor_1", (10, 10), "poor_district", "residential")
    shelter_units = [
        HousingUnit("shelter_1_1", 50, 0.2),
        HousingUnit("shelter_1_2", 50, 0.2),
        HousingUnit("shelter_1_3", 50, 0.2),
        HousingUnit("shelter_1_4", 50, 0.2),
        HousingUnit("shelter_1_5", 50, 0.2),
    ]
    shelter = ResidentialBuilding("shelter_1", shelter_plot, shelter_units, 0.2)
    poor_plots.append(shelter_plot)
    
    # Commercial plot with liquor store  
    liquor_plot = Plot("plot_poor_2", (20, 15), "poor_district", "commercial")
    liquor_store = LiquorStore("liquor_1", liquor_plot, 15.0)  # $15 per unit
    poor_plots.append(liquor_plot)
    
    # Industrial plot with factory
    factory_plot = Plot("plot_poor_3", (15, 25), "poor_district", "industrial")
    factory_jobs = [
        JobOpening("factory_job_1", "Factory Worker", 800, 0.2, 0.7),
        JobOpening("factory_job_2", "Factory Worker", 800, 0.2, 0.7),
        JobOpening("factory_job_3", "Factory Worker", 800, 0.2, 0.7),
    ]
    factory = Employer("factory_1", factory_plot, "City Factory", factory_jobs)
    poor_plots.append(factory_plot)
    
    poor_district.plots = poor_plots
    districts.append(poor_district)
    
    # Middle-class district
    middle_district = District(
        district_id="middle_district", 
        name="Downtown",
        wealth_level=3,
        plots=[]
    )
    
    # Create plots and buildings for middle district
    middle_plots = []
    
    # Apartment building
    apt_plot = Plot("plot_mid_1", (60, 40), "middle_district", "residential")
    apt_units = [
        HousingUnit(f"apt_1_{i}", 120, 0.6) for i in range(1, 11)  # 10 units
    ]
    apartments = ResidentialBuilding("apartments_1", apt_plot, apt_units, 0.6)
    middle_plots.append(apt_plot)
    
    # Casino
    casino_plot = Plot("plot_mid_2", (70, 50), "middle_district", "commercial")
    casino_games = [
        GamblingGame("Blackjack", 10, 100, 0.45, 2.0, 0.05),  # 45% win rate, 2x payout
        GamblingGame("Slot Machine", 5, 50, 0.15, 5.0, 0.15),  # 15% win rate, 5x payout
    ]
    casino = Casino("casino_1", casino_plot, casino_games, 0.05)
    middle_plots.append(casino_plot)
    
    # Office building
    office_plot = Plot("plot_mid_3", (80, 45), "middle_district", "commercial")
    office_jobs = [
        JobOpening("office_job_1", "Office Worker", 1200, 0.5, 0.4),
        JobOpening("office_job_2", "Office Worker", 1200, 0.5, 0.4),
    ]
    office = Employer("office_1", office_plot, "Downtown Office", office_jobs)
    middle_plots.append(office_plot)
    
    middle_district.plots = middle_plots
    districts.append(middle_district)
    
    # Wealthy district
    wealthy_district = District(
        district_id="wealthy_district",
        name="Hillcrest", 
        wealth_level=5,
        plots=[]
    )
    
    # Create plots and buildings for wealthy district
    wealthy_plots = []
    
    # Luxury condos
    condo_plot = Plot("plot_rich_1", (120, 80), "wealthy_district", "residential")
    condo_units = [
        HousingUnit(f"condo_1_{i}", 200, 0.9) for i in range(1, 6)  # 5 luxury units
    ]
    condos = ResidentialBuilding("condos_1", condo_plot, condo_units, 0.9)
    wealthy_plots.append(condo_plot)
    
    # Corporate headquarters
    corp_plot = Plot("plot_rich_2", (130, 90), "wealthy_district", "commercial")
    corp_jobs = [
        JobOpening("exec_job_1", "Executive", 2500, 0.8, 0.3),
        JobOpening("exec_job_2", "Manager", 2000, 0.7, 0.4),
    ]
    corp_hq = Employer("corp_1", corp_plot, "Corporate HQ", corp_jobs)
    wealthy_plots.append(corp_plot)
    
    wealthy_district.plots = wealthy_plots
    districts.append(wealthy_district)
    
    city = City("Demo City", districts)
    print(f"Created city with {len(districts)} districts and {sum(len(d.plots) for d in districts)} plots")
    
    return city


def create_demo_simulation() -> Simulation:
    """Create a demo simulation with agents."""
    print("Setting up demo simulation...")
    
    # Create city
    city = create_demo_city()
    
    # Configure simulation
    config = SimulationConfig(
        max_months=24,  # Run for 2 years
        rounds_per_month=8,
        max_agents=50,  # Start with smaller population for demo
        enable_logging=True,
        log_level="INFO"
    )
    
    # Create simulation
    simulation = Simulation(city, config)
    
    # Generate population
    print("Generating agent population...")
    
    # Generate diverse population using QuickPopulationFactory
    agents = QuickPopulationFactory.create_mixed_population(
        size=40,  # Start with 40 agents
        vulnerable_proportion=0.3,  # 30% vulnerable to addiction
        seed=42  # For reproducible results
    )
    
    # Place agents in city (simplified placement)
    available_housing = []
    for district in city.districts:
        for plot in district.plots:
            if isinstance(plot.building, ResidentialBuilding):
                # Get available units from the building
                available_units = plot.building.get_available_units()
                available_housing.extend(available_units)
    
    # Assign housing to some agents
    for i, agent in enumerate(agents[:len(available_housing)]):
        if i < len(available_housing):
            housing_unit = available_housing[i]
            housing_unit.occupied_by = agent.id
            agent.home = housing_unit
    
    # Assign jobs to some agents
    available_employers = []
    for district in city.districts:
        for plot in district.plots:
            if isinstance(plot.building, Employer):
                available_employers.append(plot.building)
    
    employed_count = 0
    for agent in agents:
        if employed_count < len(available_employers) * 2:  # Some job competition
            employer = available_employers[employed_count % len(available_employers)]
            if employer.jobs:  # Check if employer has jobs
                employment = employer.hire_agent(agent)
                if employment:
                    agent.employment = employment
                    employed_count += 1
    
    # Add agents to simulation
    simulation.add_agents(agents)
    
    print(f"Created simulation with {len(agents)} agents")
    print(f"Housing rate: {sum(1 for a in agents if a.home) / len(agents):.1%}")
    print(f"Employment rate: {sum(1 for a in agents if a.employment) / len(agents):.1%}")
    
    return simulation


def run_simulation_with_dashboard():
    """Run simulation with real-time dashboard."""
    print("=" * 60)
    print("SIMULACRA REAL-TIME VISUALIZATION DEMO")
    print("Phase 8.1: Real-time Visualization Implementation")
    print("=" * 60)
    
    # Create simulation
    simulation = create_demo_simulation()
    
    # Create metrics collector
    metrics_collector = MetricsCollector()
    
    # Create and start dashboard
    print("\nStarting real-time dashboard...")
    dashboard = RealtimeDashboard(
        simulation=simulation,
        metrics_collector=metrics_collector,
        port=5000,
        update_interval=1.0,  # Update every second
        debug=False
    )
    
    try:
        # Start dashboard
        dashboard.start(threaded=True)
        
        print(f"\n🌐 Dashboard URL: {dashboard.get_dashboard_url()}")
        print("\n📊 Dashboard Features:")
        print("  • City map with agent locations")
        print("  • Real-time agent state indicators") 
        print("  • Building occupancy tracking")
        print("  • Heat maps (stress, addiction, wealth)")
        print("  • Population metrics")
        print("  • Interactive controls")
        
        print(f"\n🚀 Starting simulation...")
        print("   💡 Open the dashboard URL in your browser to see real-time visualization")
        
        # Run simulation in background thread
        def run_simulation():
            try:
                simulation.run()
            except KeyboardInterrupt:
                print("\nSimulation interrupted")
            except Exception as e:
                print(f"Simulation error: {e}")
        
        sim_thread = threading.Thread(target=run_simulation, daemon=True)
        sim_thread.start()
        
        # Keep main thread alive and show status updates
        print("\n📈 Simulation Status:")
        print("   Press Ctrl+C to stop")
        print("-" * 40)
        
        try:
            while simulation.is_running:
                status = dashboard.get_status()
                
                print(f"\r⏱️  Month: {simulation.months_completed:2d} | "
                      f"Agents: {status['total_agents']:2d} | "
                      f"Dashboard: {'🟢' if status['is_running'] else '🔴'} | "
                      f"Simulation: {'🟢' if status['simulation_running'] else '🔴'}", 
                      end="", flush=True)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping simulation...")
            simulation.stop()
        
        # Wait for simulation to finish
        if sim_thread.is_alive():
            sim_thread.join(timeout=5)
        
        # Export final data
        print("\n💾 Exporting dashboard data...")
        export_path = dashboard.export_current_data()
        
        print(f"\n✅ Simulation completed!")
        print(f"   📁 Data exported to: {export_path}")
        print(f"   🌐 Dashboard still accessible at: {dashboard.get_dashboard_url()}")
        print("   🔧 You can continue to explore the final state")
        
        # Keep dashboard running for exploration
        input("\nPress Enter to stop dashboard and exit...")
        
    finally:
        # Clean shutdown
        dashboard.stop()
        print("\n👋 Dashboard stopped. Demo complete!")


def run_headless_demo():
    """Run a simpler headless demo for testing without web browser."""
    print("Running headless visualization demo...")
    
    simulation = create_demo_simulation()
    metrics_collector = MetricsCollector()
    
    # Create dashboard but don't start web server
    from src.visualization.data_streamer import DataStreamer
    data_streamer = DataStreamer(simulation, metrics_collector)
    
    # Test data collection
    print("\nTesting data collection...")
    
    # Collect some metrics
    from datetime import datetime
    current_time = datetime.now()
    
    for agent in simulation.agents:
        metrics_collector.collect_agent_metrics(agent, current_time)
    
    pop_metrics = metrics_collector.collect_population_metrics(simulation.agents, current_time)
    
    # Test data streaming
    city_layout = data_streamer.get_city_layout_data()
    realtime_data = data_streamer.get_realtime_data()
    
    print(f"✅ City layout: {len(city_layout['districts'])} districts, {len(city_layout['buildings'])} buildings")
    print(f"✅ Agent data: {len(realtime_data['agents'])} agents")
    print(f"✅ Population metrics: {pop_metrics.total_agents} agents, {pop_metrics.employment_rate:.1%} employed")
    print(f"✅ Heat map data: {len(realtime_data['heat_map_data']['stress'])} stress points")
    
    print("\n🎉 Headless demo completed successfully!")
    print("   All visualization components are working correctly.")
    print("   Run with dashboard=True to see the web interface.")


if __name__ == "__main__":
    import sys
    
    # Check if Flask is available
    try:
        import flask
        import flask_socketio
        web_available = True
    except ImportError:
        web_available = False
    
    if len(sys.argv) > 1 and sys.argv[1] == "--headless" or not web_available:
        if not web_available:
            print("⚠️  Flask not available. Running headless demo.")
            print("   Install Flask for full web dashboard: pip install flask flask-socketio")
        run_headless_demo()
    else:
        print("💡 Starting full web dashboard demo...")
        print("   Use --headless flag for simpler demo without web interface")
        run_simulation_with_dashboard() 
