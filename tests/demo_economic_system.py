"""
Demo script for Phase 5.3: Economic System
Shows city-wide economic parameters, job market dynamics, 
housing market availability, and price fluctuations.
"""
import numpy as np
from src.simulation import EconomyManager
from src.environment import City, District, Plot
from src.environment.buildings import Employer, ResidentialBuilding, LiquorStore, Casino
from src.environment.buildings.employer import JobOpening
from src.environment.buildings.residential import HousingUnit
from src.environment.buildings.casino import GamblingGame
from src.utils.types import (
    DistrictID, PlotID, EmployerID, BuildingID, 
    Coordinate, JobID, UnitID, PlotType
)


def create_demo_city() -> City:
    """Create a city with various economic elements."""
    # Create districts with different wealth levels
    downtown = District(
        district_id=DistrictID("downtown"),
        name="Downtown",
        wealth_level=0.8,
        plots=[]
    )
    
    suburbs = District(
        district_id=DistrictID("suburbs"),
        name="Suburbs", 
        wealth_level=0.6,
        plots=[]
    )
    
    industrial = District(
        district_id=DistrictID("industrial"),
        name="Industrial",
        wealth_level=0.3,
        plots=[]
    )
    
    # Add plots and buildings to districts
    plot_id = 0
    
    # Downtown - high-end jobs and expensive housing
    for i in range(3):
        plot = Plot(
            plot_id=PlotID(f"plot_{plot_id}"),
            location=(i * 10, 0),
            district=downtown.id,
            plot_type=PlotType.EMPLOYER if i == 0 else (PlotType.RESIDENTIAL_APARTMENT if i == 1 else PlotType.CASINO)
        )
        
        if i == 0:
            # Tech company with high-paying jobs
            jobs = [
                JobOpening(
                    job_id=JobID(f"job_{j}"),
                    title="Software Engineer",
                    monthly_salary=5000 + j * 500,
                    required_skills=0.8,
                    stress_level=0.6
                ) for j in range(5)
            ]
            employer = Employer(
                building_id=EmployerID("tech_corp"),
                plot=plot,
                company_name="TechCorp",
                jobs=jobs
            )
            plot.building = employer
            
        elif i == 1:
            # Luxury apartments
            units = [
                HousingUnit(
                    unit_id=UnitID(f"unit_dt_{j}"),
                    monthly_rent=2000 + j * 200,
                    quality=0.9,
                    occupied_by=None
                ) for j in range(10)
            ]
            residential = ResidentialBuilding(
                building_id=BuildingID("luxury_apts"),
                plot=plot,
                units=units,
                building_quality=0.9
            )
            plot.building = residential
            
        else:
            # Casino
            games = [
                GamblingGame(
                    name="Slot Machine",
                    min_bet=5.0,
                    max_bet=100.0,
                    base_win_probability=0.45,
                    payout_ratio=2.0,
                    near_miss_probability=0.1
                ),
                GamblingGame(
                    name="Blackjack",
                    min_bet=10.0,
                    max_bet=500.0,
                    base_win_probability=0.48,
                    payout_ratio=2.0,
                    near_miss_probability=0.05
                ),
                GamblingGame(
                    name="Roulette",
                    min_bet=20.0,
                    max_bet=1000.0,
                    base_win_probability=0.47,
                    payout_ratio=2.0,
                    near_miss_probability=0.08
                )
            ]
            casino = Casino(
                building_id=BuildingID("downtown_casino"),
                plot=plot,
                games=games,
                house_edge=0.05
            )
            plot.building = casino
            
        downtown.plots.append(plot)
        plot_id += 1
    
    # Suburbs - medium jobs and housing
    for i in range(4):
        plot = Plot(
            plot_id=PlotID(f"plot_{plot_id}"),
            location=(i * 10, 20),
            district=suburbs.id,
            plot_type=PlotType.EMPLOYER if i % 2 == 0 else PlotType.RESIDENTIAL_APARTMENT
        )
        
        if i % 2 == 0:
            # Retail jobs
            jobs = [
                JobOpening(
                    job_id=JobID(f"job_{plot_id}_{j}"),
                    title="Retail Worker",
                    monthly_salary=2500,
                    required_skills=0.3,
                    stress_level=0.4
                ) for j in range(3)
            ]
            employer = Employer(
                building_id=EmployerID(f"retail_{plot_id}"),
                plot=plot,
                company_name="MegaMart",
                jobs=jobs
            )
            plot.building = employer
        else:
            # Middle-class housing
            units = [
                HousingUnit(
                    unit_id=UnitID(f"unit_sub_{plot_id}_{j}"),
                    monthly_rent=1000 + j * 50,
                    quality=0.6,
                    occupied_by=None
                ) for j in range(15)
            ]
            residential = ResidentialBuilding(
                building_id=BuildingID(f"suburb_apts_{plot_id}"),
                plot=plot,
                units=units,
                building_quality=0.6
            )
            plot.building = residential
            
        suburbs.plots.append(plot)
        plot_id += 1
    
    # Industrial - low-wage jobs and cheap housing
    for i in range(3):
        plot = Plot(
            plot_id=PlotID(f"plot_{plot_id}"),
            location=(i * 10, 40),
            district=industrial.id,
            plot_type=PlotType.EMPLOYER if i == 0 else (PlotType.RESIDENTIAL_APARTMENT if i == 1 else PlotType.LIQUOR_STORE)
        )
        
        if i == 0:
            # Factory jobs
            jobs = [
                JobOpening(
                    job_id=JobID(f"job_factory_{j}"),
                    title="Factory Worker",
                    monthly_salary=2000,
                    required_skills=0.2,
                    stress_level=0.7
                ) for j in range(10)
            ]
            employer = Employer(
                building_id=EmployerID("factory"),
                plot=plot,
                company_name="Industrial Co",
                jobs=jobs
            )
            plot.building = employer
            
        elif i == 1:
            # Low-income housing
            units = [
                HousingUnit(
                    unit_id=UnitID(f"unit_ind_{j}"),
                    monthly_rent=500 + j * 20,
                    quality=0.3,
                    occupied_by=None
                ) for j in range(20)
            ]
            residential = ResidentialBuilding(
                building_id=BuildingID("affordable_housing"),
                plot=plot,
                units=units,
                building_quality=0.3
            )
            plot.building = residential
            
        else:
            # Liquor store
            liquor_store = LiquorStore(
                building_id=BuildingID("industrial_liquor"),
                plot=plot,
                alcohol_price=4.0  # Cheaper in poor areas
            )
            plot.building = liquor_store
            
        industrial.plots.append(plot)
        plot_id += 1
    
    return City(
        name="Demo City",
        districts=[downtown, suburbs, industrial]
    )


def demo_economic_cycles():
    """Demonstrate economic cycles over 12 months."""
    print("=== Economic System Demo ===\n")
    
    # Create city and economy
    city = create_demo_city()
    economy = city.global_economy
    
    print("Initial Economic State:")
    summary = economy.get_economic_summary()
    print(f"Unemployment Rate: {summary['indicators']['unemployment_rate']:.1%}")
    print(f"Consumer Confidence: {summary['indicators']['consumer_confidence']:.2f}")
    print(f"Base Salary: ${summary['prices']['salary']:.2f}")
    print(f"Base Rent: ${summary['prices']['rent']:.2f}\n")
    
    print("-" * 60)
    print("Monthly Economic Updates:")
    print("-" * 60)
    
    # Simulate 12 months
    for month in range(12):
        # Update economy
        economy.update_monthly(city)
        
        # Apply economic shock in month 6
        if month == 6:
            print("\n*** ECONOMIC SHOCK: Recession hits! ***\n")
            economy.apply_economic_shock('recession', magnitude=0.7)
        
        # Get current state
        summary = economy.get_economic_summary()
        
        # Print monthly summary
        print(f"\nMonth {month + 1}:")
        print(f"  Unemployment: {summary['indicators']['unemployment_rate']:.1%}")
        print(f"  Job Market Score: {summary['job_market']['conditions_score']:.2f}")
        print(f"  Housing Vacancy: {summary['housing_market']['vacancy_rate']:.1%}")
        print(f"  Avg Salary: ${summary['prices']['salary']:.2f}")
        print(f"  Avg Rent: ${summary['prices']['rent']:.2f}")
        print(f"  Consumer Confidence: {summary['indicators']['consumer_confidence']:.2f}")
        
    print("\n" + "-" * 60)
    print("Economic Trends Summary:")
    print("-" * 60)
    print("The simulation shows how economic indicators change over time,")
    print("especially after the recession shock in month 6.")


def demo_district_economics():
    """Show how economics vary by district."""
    print("\n=== District Economic Variations ===\n")
    
    city = create_demo_city()
    economy = city.global_economy
    
    # Update to populate statistics
    economy.update_monthly(city)
    
    # Display district-specific information
    for district in city.districts:
        print(f"\n{district.name} District (Wealth Level: {district.wealth_level:.1f}):")
        print("-" * 40)
        
        # Count jobs and housing
        total_jobs = 0
        avg_salary = 0
        salary_count = 0
        
        total_units = 0
        avg_rent = 0
        rent_count = 0
        
        for plot in district.plots:
            if hasattr(plot, 'building'):
                building = plot.building
                
                if hasattr(building, 'jobs'):  # Employer
                    for job in building.jobs:
                        total_jobs += 1
                        avg_salary += job.monthly_salary
                        salary_count += 1
                        
                elif hasattr(building, 'units'):  # Residential
                    for unit in building.units:
                        total_units += 1
                        avg_rent += unit.monthly_rent
                        rent_count += 1
        
        if salary_count > 0:
            avg_salary /= salary_count
        if rent_count > 0:
            avg_rent /= rent_count
            
        print(f"  Total Jobs: {total_jobs}")
        print(f"  Average Salary: ${avg_salary:.2f}")
        print(f"  Total Housing Units: {total_units}")
        print(f"  Average Rent: ${avg_rent:.2f}")
        
        # Show district-specific rent from economy tracker
        if district.name in economy.housing_market.rent_by_district:
            tracked_rent = economy.housing_market.rent_by_district[district.name]
            print(f"  Economy-Tracked Avg Rent: ${tracked_rent:.2f}")


def demo_price_multipliers():
    """Show how price multipliers work with economic conditions."""
    print("\n=== Price Multiplier System ===\n")
    
    economy = EconomyManager()
    
    # Show initial multipliers
    print("Initial Price Multipliers (all should be 1.0):")
    print("-" * 40)
    for good in ['salary', 'rent', 'alcohol', 'food', 'entertainment']:
        multiplier = economy.get_price_multiplier(good)
        print(f"  {good}: {multiplier:.3f}")
    
    # Simulate boom conditions
    print("\n\nApplying Economic Boom...")
    economy.apply_economic_shock('boom', magnitude=0.8)
    
    # Update a few times to see effects
    city = create_demo_city()
    for _ in range(3):
        economy.update_monthly(city)
    
    print("\nPrice Multipliers After Boom:")
    print("-" * 40)
    for good in ['salary', 'rent', 'alcohol', 'food', 'entertainment']:
        multiplier = economy.get_price_multiplier(good)
        current_price = economy.current_prices[good]
        print(f"  {good}: {multiplier:.3f} (${current_price:.2f})")
    
    # Show market condition scores
    print(f"\nMarket Condition Scores:")
    print(f"  Job Market: {economy.get_job_market_conditions():.2f}")
    print(f"  Housing Market: {economy.get_housing_market_conditions():.2f}")


def demo_economic_shocks():
    """Demonstrate different types of economic shocks."""
    print("\n=== Economic Shock Effects ===\n")
    
    # Test different shock types
    shock_types = [
        ('recession', 0.8, "Major recession"),
        ('boom', 0.6, "Economic boom"),
        ('housing_crisis', 0.7, "Housing market crash")
    ]
    
    for shock_type, magnitude, description in shock_types:
        print(f"\n{description} (magnitude: {magnitude}):")
        print("-" * 40)
        
        # Create fresh economy
        economy = EconomyManager()
        city = create_demo_city()
        
        # Get baseline
        economy.update_monthly(city)
        before = economy.get_economic_summary()
        
        # Apply shock
        economy.apply_economic_shock(shock_type, magnitude)
        economy.update_monthly(city)
        after = economy.get_economic_summary()
        
        # Compare key metrics
        print(f"  Unemployment: {before['indicators']['unemployment_rate']:.1%} → {after['indicators']['unemployment_rate']:.1%}")
        print(f"  Consumer Confidence: {before['indicators']['consumer_confidence']:.2f} → {after['indicators']['consumer_confidence']:.2f}")
        print(f"  Market Volatility: {before['indicators']['market_volatility']:.2f} → {after['indicators']['market_volatility']:.2f}")


if __name__ == "__main__":
    # Run all demos
    demo_economic_cycles()
    demo_district_economics()
    demo_price_multipliers()
    demo_economic_shocks()
    
    print("\n" + "=" * 60)
    print("=== Economic System Demo Complete ===")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✓ City-wide economic parameters tracking")
    print("✓ Job market dynamics with unemployment rates")
    print("✓ Housing market with vacancy tracking")
    print("✓ Price fluctuations based on supply/demand")
    print("✓ Economic shocks (recession/boom)")
    print("✓ District-based economic variations")
    print("✓ Price multiplier system for dynamic costs") 