"""
Demo of Phase 5.1 Time Management System

Demonstrates:
- Monthly simulation cycles
- Action round system within months
- Start/end of month events (rent, salary)
- Time progression mechanics
- Statistics tracking
- Event handling
"""
import logging
from typing import List

from src.simulation import Simulation, SimulationConfig, TimeEvent
from src.agents.agent import Agent
from src.environment.city import City
from src.environment.district import District
from src.environment.plot import Plot
from src.environment.buildings.residential import ResidentialBuilding, HousingUnit
from src.environment.buildings.employer import Employer, JobOpening
from src.utils.types import (
    PlotID, DistrictID, DistrictWealth, EmploymentInfo, 
    HousingInfo, EmployerID, JobID, UnitID, PlotType
)


def create_demo_city() -> City:
    """Create a simple city for demonstration."""
    print("Setting up demo city...")
    
    # Create a simple plot
    plot1 = Plot(
        plot_id=PlotID("demo_plot_1"),
        location=(0.0, 0.0),
        district=DistrictID("demo_district"),
        plot_type=PlotType.RESIDENTIAL_APARTMENT
    )
    
    # Create housing units
    units = [
        HousingUnit(
            unit_id=UnitID("unit_1"),
            monthly_rent=800.0,
            quality=0.6
        ),
        HousingUnit(
            unit_id=UnitID("unit_2"),
            monthly_rent=750.0,
            quality=0.5
        ),
        HousingUnit(
            unit_id=UnitID("unit_3"),
            monthly_rent=900.0,
            quality=0.7
        )
    ]
    
    # Add residential building
    residential = ResidentialBuilding(
        building_id="residential_1",
        plot=plot1,
        units=units,
        building_quality=0.6
    )
    plot1.building = residential
    
    # Create employer plot
    plot2 = Plot(
        plot_id=PlotID("demo_plot_2"),
        location=(1.0, 0.0),
        district=DistrictID("demo_district"),
        plot_type=PlotType.EMPLOYER
    )
    
    # Add employer
    job_opening = JobOpening(
        job_id=JobID("job_1"),
        title="Demo Job",
        monthly_salary=2000.0,
        required_skills=0.5,
        stress_level=0.4
    )
    
    employer = Employer(
        building_id=EmployerID("employer_1"),
        plot=plot2,
        company_name="Demo Corp",
        jobs=[job_opening]
    )
    plot2.building = employer
    
    # Create district
    district = District(
        district_id=DistrictID("demo_district"),
        name="Demo District",
        wealth_level=DistrictWealth.WORKING_CLASS,
        plots=[plot1, plot2]
    )
    
    # Create city
    city = City(
        name="Demo City",
        districts=[district]
    )
    
    print(f"Created city with {len(city.districts)} districts and {len(city._plot_index)} plots")
    return city


def create_demo_agents(city: City) -> List[Agent]:
    """Create agents with housing and employment."""
    print("Creating demo agents...")
    
    agents = []
    
    # Get the residential building and employer
    residential_plot = city.get_plot(PlotID("demo_plot_1"))
    employer_plot = city.get_plot(PlotID("demo_plot_2"))
    
    residential_building = residential_plot.building
    employer_building = employer_plot.building
    
    for i in range(3):
        # Create agent
        agent = Agent.create_with_profile(
            profile_type='balanced',
            name=f"Agent_{i+1}",
            initial_wealth=1500.0,
            initial_location=residential_plot.id
        )
        
        # Give agent housing
        if i < len(residential_building.units):
            unit = residential_building.units[i]
            agent.home = HousingInfo(
                plot_id=residential_plot.id,
                unit_id=unit.id,
                housing_quality=unit.quality,
                monthly_rent=unit.monthly_rent
            )
            # Mark unit as occupied
            unit.occupied_by = agent.id
            
        # Give agent employment (first 2 agents get jobs)
        if i < 2 and employer_building.jobs:
            job = employer_building.jobs[0]
            agent.employment = EmploymentInfo(
                employer_id=employer_building.id,
                job_id=job.id,
                job_quality=0.7,  # Derived from stress level
                base_salary=job.monthly_salary
            )
            
        agents.append(agent)
        
    print(f"Created {len(agents)} agents")
    print(f"- {sum(1 for a in agents if a.home)} have housing")
    print(f"- {sum(1 for a in agents if a.employment)} have employment")
    
    return agents


def custom_event_handler(event_type: TimeEvent, agents: List[Agent], time_manager) -> None:
    """Custom event handler to demonstrate event system."""
    if event_type == TimeEvent.MONTH_START:
        print(f"\n🎯 CUSTOM EVENT: Month {time_manager.current_time.month} started!")
        print(f"   Active agents: {len(agents)}")
        
    elif event_type == TimeEvent.SALARY_PAYMENT:
        employed_count = sum(1 for agent in agents if agent.employment is not None)
        print(f"\n💰 CUSTOM EVENT: Paying salaries to {employed_count} employed agents")
        
    elif event_type == TimeEvent.RENT_DUE:
        housed_count = sum(1 for agent in agents if agent.home is not None)
        print(f"\n🏠 CUSTOM EVENT: Collecting rent from {housed_count} housed agents")


def demonstrate_time_management():
    """Main demonstration of the time management system."""
    print("=" * 60)
    print("SIMULACRA PHASE 5.1: TIME MANAGEMENT SYSTEM DEMO")
    print("=" * 60)
    
    # Setup logging to see detailed output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create demo environment
    city = create_demo_city()
    agents = create_demo_agents(city)
    
    # Configure simulation for short demo
    config = SimulationConfig(
        max_months=3,
        rounds_per_month=5,  # Shorter for demo
        enable_logging=True,
        log_level="INFO"
    )
    
    # Create simulation
    simulation = Simulation(city, config)
    
    # Add custom event handler
    simulation.add_event_handler(TimeEvent.MONTH_START, custom_event_handler)
    simulation.add_event_handler(TimeEvent.SALARY_PAYMENT, custom_event_handler)
    simulation.add_event_handler(TimeEvent.RENT_DUE, custom_event_handler)
    
    # Add agents to simulation
    simulation.add_agents(agents)
    
    print(f"\n📊 Initial simulation state:")
    print(f"   Time: Month {simulation.time_manager.current_time.month}, Year {simulation.time_manager.current_time.year}")
    print(f"   Rounds per month: {simulation.time_manager.max_rounds_per_month}")
    print(f"   Hours per round: {simulation.time_manager.action_round_hours}")
    
    # Show initial agent states
    print(f"\n👥 Initial agent states:")
    for agent in agents:
        employment_status = "Employed" if agent.employment else "Unemployed"
        housing_status = "Housed" if agent.home else "Homeless"
        print(f"   {agent.name}: ${agent.internal_state.wealth:.0f}, {employment_status}, {housing_status}")
    
    print("\n" + "="*60)
    print("STARTING SIMULATION")
    print("="*60)
    
    # Run simulation month by month to show detailed progress
    for month in range(config.max_months):
        print(f"\n🗓️  MONTH {month + 1} SIMULATION")
        print("-" * 40)
        
        # Show state at start of month
        agent_summary = simulation.get_agent_summary()
        print(f"Start of month - Employed: {agent_summary['employed_agents']}, "
              f"Housed: {agent_summary['housed_agents']}, "
              f"Avg wealth: ${agent_summary['average_wealth']:.0f}")
        
        # Run single month
        stats = simulation.run_single_month()
        
        # Show month results
        print(f"\nMonth {month + 1} Results:")
        print(f"  - Total actions: {stats.total_actions}")
        print(f"  - Salaries paid: ${stats.total_salaries_paid:.0f}")
        print(f"  - Rent collected: ${stats.total_rent_collected:.0f}")
        print(f"  - Job losses: {stats.agents_lost_jobs}")
        print(f"  - Evictions: {stats.agents_evicted}")
        
        # Show agent states at end of month
        print(f"\nAgent states at end of month:")
        for agent in agents:
            employment_status = "Employed" if agent.employment else "Unemployed"
            housing_status = "Housed" if agent.home else "Homeless"
            print(f"  {agent.name}: ${agent.internal_state.wealth:.0f}, {employment_status}, {housing_status}")
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETED")
    print("="*60)
    
    # Show final statistics
    final_summary = simulation.get_agent_summary()
    monthly_stats = simulation.get_monthly_statistics()
    
    print(f"\n📈 Final Summary:")
    print(f"   Total months simulated: {len(monthly_stats)}")
    print(f"   Final agent count: {final_summary['total_agents']}")
    print(f"   Employment rate: {final_summary['employment_rate']:.1%}")
    print(f"   Housing rate: {final_summary['housing_rate']:.1%}")
    print(f"   Average wealth: ${final_summary['average_wealth']:.0f}")
    print(f"   Average stress: {final_summary['average_stress']:.2f}")
    print(f"   Average mood: {final_summary['average_mood']:.2f}")
    
    # Show monthly progression
    print(f"\n📊 Monthly Statistics:")
    print("Month | Actions | Salaries | Rent | Job Losses | Evictions")
    print("-" * 55)
    for i, stats in enumerate(monthly_stats, 1):
        print(f"{i:5d} | {stats.total_actions:7d} | ${stats.total_salaries_paid:7.0f} | "
              f"${stats.total_rent_collected:4.0f} | {stats.agents_lost_jobs:10d} | {stats.agents_evicted:9d}")
    
    # Demonstrate time manager features
    print(f"\n⏰ Time Manager Features:")
    time_info = simulation.time_manager.get_current_time_info()
    print(f"   Current time: Month {time_info['month']}, Year {time_info['year']}")
    print(f"   Total months elapsed: {time_info['total_months']}")
    print(f"   Rounds per month: {time_info['max_rounds']}")
    print(f"   Hours per round: {time_info['round_hours']}")
    
    print(f"\n✅ Time Management System Demo Complete!")
    print(f"   Successfully demonstrated:")
    print(f"   ✓ Monthly simulation cycles")
    print(f"   ✓ Action round system within months")
    print(f"   ✓ Start/end of month events (rent, salary)")
    print(f"   ✓ Time progression mechanics")
    print(f"   ✓ Statistics tracking")
    print(f"   ✓ Event handling system")


if __name__ == "__main__":
    demonstrate_time_management() 
