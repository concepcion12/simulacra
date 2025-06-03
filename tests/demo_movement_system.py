"""
Demo of the Movement System (Phase 4.3) for Simulacra.

This demonstrates:
1. Agent movement between plots
2. Time costs for movement based on distance and stress
3. Location-based action availability
4. Finding nearest buildings and reachable locations
"""

import numpy as np
from typing import List, Dict

# Import core simulation components
from src.agents import Agent, Action, ActionContext, generate_available_actions, MovementSystem
from src.environment.city import City
from src.environment.district import District
from src.environment.plot import Plot
from src.environment.buildings.liquor_store import LiquorStore
from src.environment.buildings.casino import Casino
from src.environment.buildings.employer import Employer
from src.environment.buildings.public_space import PublicSpace
from src.environment.buildings.residential import ResidentialBuilding

from src.utils.types import (
    PlotID, DistrictID, BuildingID, Coordinate, 
    DistrictWealth, PlotType, ActionType,
    HousingInfo, EmploymentInfo
)


def create_demo_city() -> City:
    """Create a simple city with various buildings for testing."""
    # Create districts
    districts = []
    
    # Downtown district (mixed commercial)
    downtown = District(
        district_id=DistrictID("downtown"),
        name="Downtown",
        wealth_level=DistrictWealth.MIDDLE_CLASS,
        plots=[]
    )
    
    # Create plots with buildings
    plot_id = 0
    
    # Add employer
    plot = Plot(
        plot_id=PlotID(f"plot_{plot_id}"),
        location=(5.0, 5.0),
        district=downtown.id,
        plot_type=PlotType.EMPLOYER
    )
    # Create a sample job opening
    from src.environment.buildings.employer import JobOpening
    job = JobOpening(
        job_id="job_tech_1",
        title="Software Developer",
        monthly_salary=2500.0,
        required_skills=0.7,
        stress_level=0.5
    )
    plot.building = Employer(
        building_id=BuildingID("emp_1"),
        plot=plot,
        company_name="Tech Corp",
        jobs=[job]
    )
    downtown.plots.append(plot)
    plot_id += 1
    
    # Add liquor store
    plot = Plot(
        plot_id=PlotID(f"plot_{plot_id}"),
        location=(7.0, 3.0),
        district=downtown.id,
        plot_type=PlotType.LIQUOR_STORE
    )
    plot.building = LiquorStore(
        building_id=BuildingID("liquor_1"),
        plot=plot,
        alcohol_price=6.0
    )
    downtown.plots.append(plot)
    plot_id += 1
    
    # Add casino
    plot = Plot(
        plot_id=PlotID(f"plot_{plot_id}"),
        location=(10.0, 8.0),
        district=downtown.id,
        plot_type=PlotType.CASINO
    )
    # Create sample gambling games
    from src.environment.buildings.casino import GamblingGame
    slots = GamblingGame(
        name="Slot Machine",
        min_bet=5.0,
        max_bet=100.0,
        base_win_probability=0.35,
        payout_ratio=2.0,
        near_miss_probability=0.15
    )
    plot.building = Casino(
        building_id=BuildingID("casino_1"),
        plot=plot,
        games=[slots],
        house_edge=0.05
    )
    downtown.plots.append(plot)
    plot_id += 1
    
    # Add public space
    plot = Plot(
        plot_id=PlotID(f"plot_{plot_id}"),
        location=(6.0, 6.0),
        district=downtown.id,
        plot_type=PlotType.PUBLIC_SPACE
    )
    plot.building = PublicSpace(
        building_id=BuildingID("park_1"),
        plot=plot,
        space_name="Central Park"
    )
    downtown.plots.append(plot)
    plot_id += 1
    
    districts.append(downtown)
    
    # Residential district
    residential = District(
        district_id=DistrictID("residential"),
        name="Residential Area",
        wealth_level=DistrictWealth.WORKING_CLASS,
        plots=[]
    )
    
    # Add residential buildings
    for i in range(3):
        plot = Plot(
            plot_id=PlotID(f"plot_{plot_id}"),
            location=(2.0 + i*2, 10.0),
            district=residential.id,
            plot_type=PlotType.RESIDENTIAL_APARTMENT
        )
        # Create housing units
        from src.environment.buildings.residential import HousingUnit
        units = []
        for j in range(5):  # 5 units per building
            unit = HousingUnit(
                unit_id=f"unit_{i}_{j}",
                monthly_rent=800 + i*100,
                quality=0.6 + i*0.1
            )
            units.append(unit)
        
        plot.building = ResidentialBuilding(
            building_id=BuildingID(f"res_{i}"),
            plot=plot,
            units=units,
            building_quality=0.6 + i*0.1
        )
        residential.plots.append(plot)
        plot_id += 1
    
    districts.append(residential)
    
    return City(name="Demo City", districts=districts)


def get_building_name(building) -> str:
    """Get a descriptive name for a building."""
    if hasattr(building, 'space_name'):
        return building.space_name
    elif hasattr(building, 'company_name'):
        return building.company_name
    else:
        return type(building).__name__


def demo_movement_calculations(city: City, movement_system: MovementSystem):
    """Demonstrate basic movement calculations."""
    print("=== Movement Time Calculations ===\n")
    
    # Get some plot IDs for testing
    plot_ids = list(city._plot_index.keys())
    
    if len(plot_ids) >= 2:
        from_plot = plot_ids[0]
        to_plot = plot_ids[-1]
        
        # Calculate movement time with different stress levels
        for stress in [0.0, 0.5, 0.9]:
            time_cost = movement_system.calculate_movement_time(
                from_plot, to_plot, stress
            )
            print(f"Movement from {from_plot} to {to_plot}")
            print(f"  Stress level: {stress:.1f}")
            print(f"  Time cost: {time_cost:.2f} hours\n")


def demo_reachable_locations(city: City, movement_system: MovementSystem):
    """Demonstrate finding reachable locations within time budget."""
    print("=== Reachable Locations ===\n")
    
    start_plot = list(city._plot_index.keys())[0]
    time_budgets = [1.0, 3.0, 5.0]
    
    for budget in time_budgets:
        reachable = movement_system.get_plots_within_time_budget(
            start_plot, budget, agent_stress=0.3
        )
        print(f"With {budget} hours available from {start_plot}:")
        print(f"  Can reach {len(reachable)} plots")
        
        # Show some examples
        for plot_id in list(reachable)[:3]:
            plot = city.get_plot(plot_id)
            if plot and plot.building:
                print(f"    - {plot_id}: {get_building_name(plot.building)}")
        print()


def demo_nearest_buildings(city: City, movement_system: MovementSystem):
    """Demonstrate finding nearest buildings of specific types."""
    print("=== Finding Nearest Buildings ===\n")
    
    start_plot = list(city._plot_index.keys())[0]
    
    # Find nearest of each building type
    building_types = [
        (LiquorStore, "Liquor Store"),
        (Casino, "Casino"),
        (Employer, "Employer"),
        (PublicSpace, "Public Space")
    ]
    
    for building_class, name in building_types:
        result = movement_system.find_nearest_building(
            start_plot, building_class
        )
        
        if result:
            building_id, plot_id, distance = result
            plot = city.get_plot(plot_id)
            print(f"Nearest {name}:")
            print(f"  Building: {get_building_name(plot.building)}")
            print(f"  Distance: {distance:.2f} units")
            print(f"  Walking time: {distance/movement_system.movement_cost.base_speed:.2f} hours\n")


def demo_location_based_actions(city: City, movement_system: MovementSystem):
    """Demonstrate location-based action generation."""
    print("=== Location-Based Actions ===\n")
    
    # Create an agent with specific location
    agent = Agent.create_with_profile('balanced')
    agent.current_location = list(city._plot_index.keys())[0]
    agent.internal_state.wealth = 500
    agent.internal_state.stress = 0.4
    
    # Give agent a home and job for more interesting actions
    agent.home = HousingInfo(
        plot_id=PlotID("plot_5"),  # One of the residential plots
        unit_id="unit_1_0",
        housing_quality=0.6,
        monthly_rent=900
    )
    
    agent.employment = EmploymentInfo(
        employer_id=BuildingID("emp_1"),
        job_id="job_tech_1",
        job_quality=0.7,
        base_salary=2500
    )
    
    # Create context with movement system
    class MockEnvironment:
        def __init__(self, movement_system):
            self.movement_system = movement_system
    
    context = ActionContext(
        agent=agent,
        environment=MockEnvironment(movement_system)
    )
    
    # Generate available actions
    actions = generate_available_actions(agent, context)
    
    print(f"Agent at {agent.current_location}")
    print(f"Stress: {agent.internal_state.stress:.2f}")
    print(f"Wealth: ${agent.internal_state.wealth:.2f}")
    print(f"Time budget: {agent.action_budget.remaining_hours:.1f} hours\n")
    
    print("Available actions:")
    for action in actions:
        print(f"\n- {action.action_type.name}")
        print(f"  Time cost: {action.time_cost:.2f} hours")
        if action.target:
            print(f"  Target location: {action.target}")
            target_plot = city.get_plot(action.target)
            if target_plot and target_plot.building:
                print(f"  Target building: {get_building_name(target_plot.building)}")


def demo_action_targets(city: City, movement_system: MovementSystem):
    """Demonstrate finding action targets within time budget."""
    print("\n=== Action Targets Within Budget ===\n")
    
    start_plot = list(city._plot_index.keys())[0]
    time_budget = 4.0
    
    action_types = [ActionType.DRINK, ActionType.GAMBLE, ActionType.BEG]
    
    for action_type in action_types:
        targets = movement_system.get_available_action_targets(
            start_plot, action_type, time_budget, agent_stress=0.3
        )
        
        print(f"{action_type.name} targets within {time_budget} hours:")
        for building_id, plot_id, travel_time in targets:
            plot = city.get_plot(plot_id)
            if plot and plot.building:
                print(f"  - {get_building_name(plot.building)}: {travel_time:.2f}h away")
        
        if not targets:
            print("  - No reachable targets")
        print()


def demo_movement_options(city: City, movement_system: MovementSystem):
    """Demonstrate movement options for an agent."""
    print("=== Movement Options ===\n")
    
    start_plot = list(city._plot_index.keys())[0]
    
    # Create important locations dict
    important_locations = {
        'home': PlotID("plot_5"),
        'work': PlotID("plot_0")
    }
    
    options = movement_system.get_movement_options(
        start_plot,
        time_budget=5.0,
        agent_stress=0.2,
        important_locations=important_locations
    )
    
    print(f"Movement options from {start_plot}:")
    for plot_id, travel_time, description in options[:8]:
        print(f"  - {description}: {travel_time:.2f} hours")


def main():
    """Run the movement system demonstration."""
    print("Simulacra Movement System Demo")
    print("================================\n")
    
    # Create demo city
    city = create_demo_city()
    print(f"Created {city.name} with {len(city.districts)} districts")
    print(f"Total plots: {len(city._plot_index)}\n")
    
    # Create movement system
    movement_system = MovementSystem(city)
    
    # Run demonstrations
    demo_movement_calculations(city, movement_system)
    demo_reachable_locations(city, movement_system)
    demo_nearest_buildings(city, movement_system)
    demo_location_based_actions(city, movement_system)
    demo_action_targets(city, movement_system)
    demo_movement_options(city, movement_system)
    
    print("\nMovement system demo complete!")


if __name__ == "__main__":
    main() 