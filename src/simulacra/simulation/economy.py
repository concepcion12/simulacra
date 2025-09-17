"""
Economic system for the Simulacra simulation.
Implements Phase 5.3: Economic System with city-wide parameters,
job market dynamics, housing market availability, and price fluctuations.
"""
from typing import Dict, List
from dataclasses import dataclass, field
import random
import math
from collections import defaultdict


@dataclass
class EconomicIndicators:
    """City-wide economic indicators that affect various systems."""
    unemployment_rate: float = 0.05  # 5% baseline
    inflation_rate: float = 0.02  # 2% annual, converted to monthly
    economic_growth: float = 0.0  # Current growth rate
    consumer_confidence: float = 0.7  # [0,1] scale
    market_volatility: float = 0.1  # Price fluctuation factor
    

@dataclass 
class JobMarketState:
    """Tracks job market conditions and dynamics."""
    total_jobs: int = 0
    filled_jobs: int = 0
    job_openings: int = 0
    average_salary: float = 0.0
    salary_by_sector: Dict[str, float] = field(default_factory=dict)
    job_creation_rate: float = 0.02  # Monthly job creation
    job_destruction_rate: float = 0.015  # Monthly job loss
    

@dataclass
class HousingMarketState:
    """Tracks housing market conditions and availability."""
    total_units: int = 0
    occupied_units: int = 0
    available_units: int = 0
    average_rent: float = 0.0
    vacancy_rate: float = 0.05
    rent_by_district: Dict[str, float] = field(default_factory=dict)
    construction_rate: float = 0.005  # New units per month
    demolition_rate: float = 0.001  # Units removed per month
    

class EconomyManager:
    """
    Manages the city's economic system including job markets,
    housing markets, and price dynamics.
    """
    
    def __init__(self, base_salary: float = 3000.0, base_rent: float = 1000.0):
        """
        Initialize the economy manager.
        
        Args:
            base_salary: Baseline monthly salary
            base_rent: Baseline monthly rent
        """
        self.indicators = EconomicIndicators()
        self.job_market = JobMarketState()
        self.housing_market = HousingMarketState()
        
        # Price tracking
        self.base_prices = {
            'salary': base_salary,
            'rent': base_rent,
            'alcohol': 5.0,
            'food': 50.0,
            'entertainment': 20.0
        }
        
        self.current_prices = self.base_prices.copy()
        self.price_history: Dict[str, List[float]] = defaultdict(list)
        
        # Market cycles
        self.economic_cycle_position = 0.0  # Position in boom/bust cycle
        self.cycle_speed = 0.1  # How fast we move through cycles
        
    def update_monthly(self, city) -> None:
        """
        Update economic indicators and market states monthly.
        
        Args:
            city: The city object to analyze
        """
        # Update market information from city state
        self._update_job_market_stats(city)
        self._update_housing_market_stats(city)
        
        # Update economic indicators
        self._update_economic_indicators()
        
        # Apply economic cycles
        self._advance_economic_cycle()
        
        # Update prices based on conditions
        self._update_prices()
        
        # Record history
        self._record_price_history()
        
    def _update_job_market_stats(self, city) -> None:
        """Calculate current job market statistics from city data."""
        total_jobs = 0
        filled_jobs = 0
        total_salaries = 0.0
        sector_jobs = defaultdict(int)
        sector_salaries = defaultdict(float)
        
        # Scan all employers in the city
        for district in city.districts:
            for plot in district.plots:
                if hasattr(plot, 'building'):
                    building = plot.building
                    if hasattr(building, 'jobs'):  # It's an employer
                        for job in building.jobs:
                            total_jobs += 1
                            # Check if job is filled (simplified - would need employment tracking)
                            # For now, assume some percentage are filled
                            if random.random() < 0.8:  # 80% employment rate
                                filled_jobs += 1
                                total_salaries += job.monthly_salary
                                
                            # Track by sector (using building name as proxy)
                            sector = getattr(building, 'company_name', 'General')
                            sector_jobs[sector] += 1
                            sector_salaries[sector] += job.monthly_salary
                            
        self.job_market.total_jobs = total_jobs
        self.job_market.filled_jobs = filled_jobs
        self.job_market.job_openings = total_jobs - filled_jobs
        
        if filled_jobs > 0:
            self.job_market.average_salary = total_salaries / filled_jobs
        
        # Calculate sector averages
        for sector, count in sector_jobs.items():
            if count > 0:
                self.job_market.salary_by_sector[sector] = sector_salaries[sector] / count
                
    def _update_housing_market_stats(self, city) -> None:
        """Calculate current housing market statistics from city data."""
        total_units = 0
        occupied_units = 0  
        total_rent = 0.0
        district_units = defaultdict(int)
        district_rent = defaultdict(float)
        
        # Scan all residential buildings
        for district in city.districts:
            for plot in district.plots:
                if hasattr(plot, 'building'):
                    building = plot.building
                    if hasattr(building, 'units'):  # It's residential
                        for unit in building.units:
                            total_units += 1
                            total_rent += unit.monthly_rent
                            district_units[district.name] += 1
                            district_rent[district.name] += unit.monthly_rent
                            
                            if unit.occupied_by is not None:
                                occupied_units += 1
                                
        self.housing_market.total_units = total_units
        self.housing_market.occupied_units = occupied_units
        self.housing_market.available_units = total_units - occupied_units
        
        if total_units > 0:
            self.housing_market.average_rent = total_rent / total_units
            self.housing_market.vacancy_rate = (total_units - occupied_units) / total_units
            
        # Calculate district averages
        for district, count in district_units.items():
            if count > 0:
                self.housing_market.rent_by_district[district] = district_rent[district] / count
                
    def _update_economic_indicators(self) -> None:
        """Update city-wide economic indicators based on market conditions."""
        # Calculate unemployment rate
        if self.job_market.total_jobs > 0:
            employment_rate = self.job_market.filled_jobs / self.job_market.total_jobs
            self.indicators.unemployment_rate = 1.0 - employment_rate
        
        # Update consumer confidence based on employment and housing availability
        employment_factor = 1.0 - self.indicators.unemployment_rate
        housing_factor = 1.0 - self.housing_market.vacancy_rate
        self.indicators.consumer_confidence = 0.6 * employment_factor + 0.4 * housing_factor
        
        # Economic growth reflects job and housing market health
        job_growth = (self.job_market.job_creation_rate - self.job_market.job_destruction_rate)
        housing_growth = (self.housing_market.construction_rate - self.housing_market.demolition_rate)
        self.indicators.economic_growth = 0.7 * job_growth + 0.3 * housing_growth
        
    def _advance_economic_cycle(self) -> None:
        """Advance the position in the economic boom/bust cycle."""
        # Use sine wave for cyclical economy
        self.economic_cycle_position += self.cycle_speed
        cycle_value = math.sin(self.economic_cycle_position)
        
        # Adjust indicators based on cycle
        cycle_impact = cycle_value * 0.3  # ±30% impact
        
        # Boom periods have lower unemployment, higher confidence
        self.indicators.unemployment_rate *= (1.0 - cycle_impact)
        self.indicators.consumer_confidence *= (1.0 + cycle_impact * 0.5)
        
        # Adjust market dynamics
        self.job_market.job_creation_rate = 0.02 * (1.0 + cycle_impact)
        self.job_market.job_destruction_rate = 0.015 * (1.0 - cycle_impact * 0.5)
        
        # Market volatility increases during transitions
        transition_speed = abs(math.cos(self.economic_cycle_position))
        self.indicators.market_volatility = 0.05 + 0.15 * transition_speed
        
    def _update_prices(self) -> None:
        """Update prices based on economic conditions and market dynamics."""
        # Inflation affects all prices
        monthly_inflation = self.indicators.inflation_rate / 12.0
        
        for good, base_price in self.base_prices.items():
            # Start with inflation adjustment
            new_price = self.current_prices[good] * (1.0 + monthly_inflation)
            
            # Apply supply/demand dynamics
            if good == 'salary':
                # Salaries respond to unemployment
                unemployment_factor = 1.0 - (self.indicators.unemployment_rate - 0.05) * 2.0
                new_price *= unemployment_factor
                
            elif good == 'rent':
                # Rent responds to vacancy rate
                vacancy_factor = 1.0 + (0.05 - self.housing_market.vacancy_rate) * 3.0
                new_price *= vacancy_factor
                
            # Add market volatility
            volatility = random.gauss(0, self.indicators.market_volatility)
            new_price *= (1.0 + volatility)
            
            # Clamp to reasonable bounds (50% to 200% of base)
            new_price = max(base_price * 0.5, min(base_price * 2.0, new_price))
            
            self.current_prices[good] = new_price
            
    def _record_price_history(self) -> None:
        """Record current prices for historical tracking."""
        for good, price in self.current_prices.items():
            self.price_history[good].append(price)
            # Keep only last 12 months
            if len(self.price_history[good]) > 12:
                self.price_history[good].pop(0)
                
    def get_price_multiplier(self, good: str) -> float:
        """
        Get the current price multiplier for a good compared to base price.
        
        Args:
            good: The type of good ('salary', 'rent', 'alcohol', etc.)
            
        Returns:
            Price multiplier (1.0 = base price)
        """
        if good not in self.base_prices:
            return 1.0
            
        return self.current_prices[good] / self.base_prices[good]
        
    def get_job_market_conditions(self) -> float:
        """
        Get a score representing job market conditions.
        
        Returns:
            Score from 0 (terrible) to 1 (excellent)
        """
        # Combine unemployment rate and job availability
        employment_score = 1.0 - self.indicators.unemployment_rate
        availability_score = self.job_market.job_openings / max(1, self.job_market.total_jobs)
        
        return 0.7 * employment_score + 0.3 * availability_score
        
    def get_housing_market_conditions(self) -> float:
        """
        Get a score representing housing market conditions.
        
        Returns:
            Score from 0 (no availability) to 1 (abundant housing)
        """
        return min(1.0, self.housing_market.available_units / max(1, self.housing_market.total_units * 0.1))
        
    def apply_economic_shock(self, shock_type: str, magnitude: float) -> None:
        """
        Apply an economic shock to the system.
        
        Args:
            shock_type: Type of shock ('recession', 'boom', 'housing_crisis', etc.)
            magnitude: Severity of shock (0.0 to 1.0)
        """
        if shock_type == 'recession':
            self.indicators.economic_growth -= magnitude * 0.05
            self.indicators.consumer_confidence *= (1.0 - magnitude * 0.3)
            self.job_market.job_destruction_rate *= (1.0 + magnitude * 0.5)
            
        elif shock_type == 'boom':
            self.indicators.economic_growth += magnitude * 0.03
            self.indicators.consumer_confidence *= (1.0 + magnitude * 0.2)
            self.job_market.job_creation_rate *= (1.0 + magnitude * 0.3)
            
        elif shock_type == 'housing_crisis':
            self.housing_market.vacancy_rate *= (1.0 + magnitude * 2.0)
            self.housing_market.construction_rate *= (1.0 - magnitude * 0.5)
            
        # Increase volatility during shocks
        self.indicators.market_volatility *= (1.0 + magnitude)
        
    def get_economic_summary(self) -> Dict[str, any]:
        """Get a summary of current economic conditions."""
        return {
            'indicators': {
                'unemployment_rate': self.indicators.unemployment_rate,
                'inflation_rate': self.indicators.inflation_rate,
                'economic_growth': self.indicators.economic_growth,
                'consumer_confidence': self.indicators.consumer_confidence,
                'market_volatility': self.indicators.market_volatility
            },
            'job_market': {
                'total_jobs': self.job_market.total_jobs,
                'job_openings': self.job_market.job_openings,
                'average_salary': self.job_market.average_salary,
                'conditions_score': self.get_job_market_conditions()
            },
            'housing_market': {
                'total_units': self.housing_market.total_units,
                'available_units': self.housing_market.available_units,
                'average_rent': self.housing_market.average_rent,
                'vacancy_rate': self.housing_market.vacancy_rate,
                'conditions_score': self.get_housing_market_conditions()
            },
            'prices': self.current_prices.copy()
        } 
