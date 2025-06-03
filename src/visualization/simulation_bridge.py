"""
Simulation Bridge - Connects unified interface with existing Simulacra simulation engine
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time
import json
from datetime import datetime

# Import existing Simulacra components with correct paths
try:
    # Import from the actual module structure
    from src.environment.city import City
    from src.simulation.simulation import Simulation, SimulationConfig
    from src.simulation.economy import EconomyManager
    from src.population.population_generator import PopulationGenerator
    from src.analytics.metrics import MetricsCollector
    from src.analytics.exporters import DataExporter
    from src.agents.agent import Agent
except ImportError as e:
    print(f"Warning: Could not import simulation components: {e}")
    print("Please ensure all simulation modules are properly installed")
    City = None
    Simulation = None
    SimulationConfig = None
    EconomyManager = None
    PopulationGenerator = None
    MetricsCollector = None
    DataExporter = None
    Agent = None


class SimulationBridge:
    """
    Bridge between the unified interface and the existing simulation engine.
    Translates UI configurations into simulation parameters and manages execution.
    """
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.active_simulations = {}
        self.simulation_threads = {}
        print(f"SimulationBridge initialized. Dependencies available: {self._check_dependencies()}")
    
    def create_simulation_from_config(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Create and start a simulation from UI configuration.
        
        Args:
            config: Configuration dictionary from the setup wizard
            
        Returns:
            simulation_id if successful, None if failed
        """
        print(f"Creating simulation from config: {config.get('city_name', 'Unknown')}")
        
        if not self._check_dependencies():
            print("Missing simulation dependencies - using fallback mode")
            return self._create_fallback_simulation(config)
        
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create city from configuration
            city = self._create_city_from_config(config)
            print(f"Created city: {city.name}")
            
            # Create simulation configuration
            sim_config = self._create_simulation_config_from_ui(config)
            print(f"Created simulation config for {sim_config.max_months} months")
            
            # Create the main simulation
            simulation = Simulation(city=city, config=sim_config)
            print(f"Created simulation engine")
            
            # Generate population and add to simulation
            population = self._create_population_from_config(config, city)
            simulation.agents = population
            print(f"Added {len(population)} agents to simulation")
            
            # Set up metrics collection
            metrics_collector = self._create_metrics_collector(config)
            
            # Store simulation reference
            self.active_simulations[simulation_id] = {
                'id': simulation_id,
                'simulation': simulation,
                'config': config,
                'status': 'ready',
                'created_at': datetime.now(),
                'metrics_collector': metrics_collector,
                'total_rounds': sim_config.max_months * sim_config.rounds_per_month,
                'current_round': 0
            }
            
            print(f"Simulation {simulation_id} created successfully")
            return simulation_id
            
        except Exception as e:
            print(f"Error creating simulation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_fallback_simulation(self, config: Dict[str, Any]) -> str:
        """Create a fallback simulation when dependencies are missing."""
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_simulations[simulation_id] = {
            'id': simulation_id,
            'config': config,
            'status': 'ready',
            'created_at': datetime.now(),
            'fallback_mode': True,
            'total_rounds': config.get('duration_months', 12) * config.get('rounds_per_month', 8),
            'current_round': 0
        }
        
        print(f"Created fallback simulation {simulation_id}")
        return simulation_id
    
    def start_simulation(self, simulation_id: str) -> bool:
        """Start a simulation in a background thread."""
        if simulation_id not in self.active_simulations:
            print(f"Simulation {simulation_id} not found")
            return False
        
        simulation_data = self.active_simulations[simulation_id]
        print(f"Starting simulation {simulation_id}")
        
        # Create and start simulation thread
        thread = threading.Thread(
            target=self._run_simulation_thread,
            args=(simulation_id,),
            daemon=True
        )
        
        self.simulation_threads[simulation_id] = thread
        simulation_data['status'] = 'running'
        simulation_data['started_at'] = datetime.now()
        
        thread.start()
        return True
    
    def _run_simulation_thread(self, simulation_id: str):
        """Run simulation in background thread with real-time updates."""
        simulation_data = self.active_simulations[simulation_id]
        config = simulation_data['config']
        
        print(f"Running simulation thread for {simulation_id}")
        
        try:
            update_interval = config.get('update_interval', 1.0)
            
            if simulation_data.get('fallback_mode'):
                self._run_fallback_simulation(simulation_id, update_interval)
            else:
                self._run_real_simulation(simulation_id, update_interval)
                
        except Exception as e:
            print(f"Error in simulation thread: {e}")
            import traceback
            traceback.print_exc()
            simulation_data['status'] = 'error'
            simulation_data['error'] = str(e)
            
            if self.socketio:
                self.socketio.emit('simulation_error', {
                    'simulation_id': simulation_id,
                    'error': str(e)
                })
    
    def _run_real_simulation(self, simulation_id: str, update_interval: float):
        """Run actual simulation with real components."""
        simulation_data = self.active_simulations[simulation_id]
        simulation = simulation_data['simulation']
        total_rounds = simulation_data['total_rounds']
        
        # Set simulation to running state
        simulation.is_running = True
        
        # Run simulation month by month
        for month in range(simulation.config.max_months):
            if simulation_data['status'] != 'running':
                break
                
            print(f"Running month {month + 1}/{simulation.config.max_months}")
            
            # Run one month of simulation
            month_stats = simulation.run_single_month()
            simulation_data['current_round'] = (month + 1) * simulation.config.rounds_per_month
            
            # Emit real-time update via WebSocket
            if self.socketio:
                progress = (month + 1) / simulation.config.max_months
                update_data = {
                    'simulation_id': simulation_id,
                    'month': month + 1,
                    'total_months': simulation.config.max_months,
                    'progress': progress,
                    'metrics': self._extract_metrics_from_stats(month_stats)
                }
                self.socketio.emit('simulation_update', update_data)
                print(f"Sent update for month {month + 1}, progress: {progress:.1%}")
            
            # Sleep to control update rate
            time.sleep(update_interval)
        
        # Simulation completed
        simulation.is_running = False
        simulation_data['status'] = 'completed'
        simulation_data['completed_at'] = datetime.now()
        
        if self.socketio:
            self.socketio.emit('simulation_complete', {
                'simulation_id': simulation_id,
                'status': 'completed'
            })
        
        print(f"Simulation {simulation_id} completed successfully")
    
    def _run_fallback_simulation(self, simulation_id: str, update_interval: float):
        """Run a fallback simulation that generates mock data."""
        simulation_data = self.active_simulations[simulation_id]
        config = simulation_data['config']
        total_months = config.get('duration_months', 12)
        
        import random
        
        for month in range(total_months):
            if simulation_data['status'] != 'running':
                break
                
            # Generate mock metrics
            progress = (month + 1) / total_months
            mock_metrics = {
                'employment_rate': 0.85 - (random.random() * 0.3 * progress),
                'average_wealth': 1000 + random.randint(-200, 200),
                'addiction_rate': 0.15 + (random.random() * 0.2 * progress),
                'homelessness_rate': 0.05 + (random.random() * 0.15 * progress),
                'total_agents': config.get('total_agents', 100)
            }
            
            simulation_data['current_round'] = (month + 1) * config.get('rounds_per_month', 8)
            
            # Emit real-time update
            if self.socketio:
                update_data = {
                    'simulation_id': simulation_id,
                    'month': month + 1,
                    'total_months': total_months,
                    'progress': progress,
                    'metrics': mock_metrics
                }
                self.socketio.emit('simulation_update', update_data)
                print(f"Sent fallback update for month {month + 1}")
            
            time.sleep(update_interval)
        
        # Mark as completed
        simulation_data['status'] = 'completed' 
        simulation_data['completed_at'] = datetime.now()
        
        if self.socketio:
            self.socketio.emit('simulation_complete', {
                'simulation_id': simulation_id,
                'status': 'completed'
            })
    
    def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """Get current status of a simulation."""
        if simulation_id not in self.active_simulations:
            return {'error': 'Simulation not found'}
        
        simulation_data = self.active_simulations[simulation_id]
        status = {
            'id': simulation_id,
            'status': simulation_data['status'],
            'created_at': simulation_data['created_at'].isoformat()
        }
        
        if 'started_at' in simulation_data:
            status['started_at'] = simulation_data['started_at'].isoformat()
        
        if simulation_data['status'] == 'running':
            current_round = simulation_data.get('current_round', 0)
            total_rounds = simulation_data.get('total_rounds', 1)
            status.update({
                'current_round': current_round,
                'total_rounds': total_rounds,
                'progress': current_round / total_rounds if total_rounds > 0 else 0
            })
        
        if simulation_data['status'] == 'completed' and 'completed_at' in simulation_data:
            status['completed_at'] = simulation_data['completed_at'].isoformat()
        
        if simulation_data['status'] == 'error':
            status['error'] = simulation_data.get('error', 'Unknown error')
        
        return status
    
    def _create_city_from_config(self, config: Dict[str, Any]) -> 'City':
        """Create City object from UI configuration."""
        from src.environment.district import District
        from src.environment.plot import Plot
        from src.utils.types import DistrictWealth, PlotType
        from src.environment.buildings import (
            ResidentialBuilding, HousingUnit, Employer, JobOpening,
            LiquorStore, Casino
        )
        from src.environment.buildings.casino import GamblingGame
        
        buildings_config = config.get('buildings', {})
        city_name = config.get('city_name', 'Simulation City')
        
        # Create a main district
        district = District(
            district_id="main_district",
            name="Main District",
            wealth_level=DistrictWealth.MIDDLE_CLASS,
            plots=[]
        )
        
        plot_id = 0
        
        # Create residential buildings
        residential_count = buildings_config.get('residential', 10)
        for i in range(residential_count):
            plot = Plot(
                plot_id=f"plot_{plot_id}",
                location=(plot_id % 10, plot_id // 10),
                district="main_district",
                plot_type=PlotType.RESIDENTIAL_APARTMENT
            )
            
            # Create housing units for this building
            units = []
            for j in range(4):  # 4 units per building
                unit = HousingUnit(
                    unit_id=f"unit_{plot_id}_{j}",
                    monthly_rent=800 + (i * 50),  # Varying rent
                    quality=0.5 + (i * 0.01)  # Slightly varying quality
                )
                units.append(unit)
            
            # Create the residential building
            building = ResidentialBuilding(
                building_id=f"residential_{plot_id}",
                plot=plot,
                units=units,
                building_quality=0.6
            )
            
            district.plots.append(plot)
            plot_id += 1
        
        # Create commercial/employer buildings
        commercial_count = buildings_config.get('commercial', 5)
        for i in range(commercial_count):
            plot = Plot(
                plot_id=f"plot_{plot_id}",
                location=(plot_id % 10, plot_id // 10),
                district="main_district",
                plot_type=PlotType.EMPLOYER
            )
            
            # Create jobs for this employer
            jobs = []
            for j in range(3):  # 3 jobs per commercial building
                job = JobOpening(
                    job_id=f"job_{plot_id}_{j}",
                    title="Office Worker",
                    monthly_salary=2000 + (i * 200),
                    required_skills=0.5,
                    stress_level=0.4
                )
                jobs.append(job)
            
            # Create the employer building
            building = Employer(
                building_id=f"employer_{plot_id}",
                plot=plot,
                company_name=f"Company_{i+1}",
                jobs=jobs
            )
            
            district.plots.append(plot)
            plot_id += 1
        
        # Create industrial buildings (more jobs, lower pay)
        industrial_count = buildings_config.get('industrial', 3)
        for i in range(industrial_count):
            plot = Plot(
                plot_id=f"plot_{plot_id}",
                location=(plot_id % 10, plot_id // 10),
                district="main_district",
                plot_type=PlotType.EMPLOYER
            )
            
            # Create jobs for this industrial employer
            jobs = []
            for j in range(5):  # 5 jobs per industrial building
                job = JobOpening(
                    job_id=f"job_{plot_id}_{j}",
                    title="Factory Worker",
                    monthly_salary=1500 + (i * 100),
                    required_skills=0.3,
                    stress_level=0.6
                )
                jobs.append(job)
            
            # Create the employer building
            building = Employer(
                building_id=f"employer_{plot_id}",
                plot=plot,
                company_name=f"Factory_{i+1}",
                jobs=jobs
            )
            
            district.plots.append(plot)
            plot_id += 1
        
        # Create casinos
        casino_count = buildings_config.get('casinos', 2)
        for i in range(casino_count):
            plot = Plot(
                plot_id=f"plot_{plot_id}",
                location=(plot_id % 10, plot_id // 10),
                district="main_district",
                plot_type=PlotType.CASINO
            )
            
            # Create gambling games
            games = [
                GamblingGame(
                    name="Blackjack",
                    min_bet=10.0,
                    max_bet=500.0,
                    base_win_probability=0.45,
                    payout_ratio=2.0,
                    near_miss_probability=0.1
                ),
                GamblingGame(
                    name="Slot Machine",
                    min_bet=5.0,
                    max_bet=100.0,
                    base_win_probability=0.15,
                    payout_ratio=10.0,
                    near_miss_probability=0.2
                )
            ]
            
            # Create the casino building
            building = Casino(
                building_id=f"casino_{plot_id}",
                plot=plot,
                games=games,
                house_edge=0.05
            )
            
            district.plots.append(plot)
            plot_id += 1
        
        # Create liquor stores
        liquor_count = buildings_config.get('liquor_stores', 5)
        for i in range(liquor_count):
            plot = Plot(
                plot_id=f"plot_{plot_id}",
                location=(plot_id % 10, plot_id // 10),
                district="main_district",
                plot_type=PlotType.LIQUOR_STORE
            )
            
            # Create the liquor store building
            building = LiquorStore(
                building_id=f"liquor_{plot_id}",
                plot=plot,
                alcohol_price=8.0 + (i * 1.0)  # Varying prices
            )
            
            district.plots.append(plot)
            plot_id += 1
        
        # Create city with the populated district
        districts = [district]
        city = City(name=city_name, districts=districts)
        
        # Calculate totals for logging
        total_housing_units = residential_count * 4
        total_jobs = (commercial_count * 3) + (industrial_count * 5)
        
        print(f"City '{city_name}' created successfully:")
        print(f"  - {len(districts)} districts")
        print(f"  - {plot_id} plots total")
        print(f"  - {residential_count} residential buildings ({total_housing_units} housing units)")
        print(f"  - {commercial_count + industrial_count} employers ({total_jobs} jobs)")
        print(f"  - {casino_count} casinos")
        print(f"  - {liquor_count} liquor stores")
        
        return city
    
    def _create_simulation_config_from_ui(self, config: Dict[str, Any]) -> 'SimulationConfig':
        """Create SimulationConfig from UI configuration."""
        return SimulationConfig(
            max_months=config.get('duration_months', 12),
            rounds_per_month=config.get('rounds_per_month', 8),
            max_agents=config.get('total_agents', 100),
            enable_logging=True,
            log_level="INFO"
        )
    
    def _create_population_from_config(self, config: Dict[str, Any], city: 'City') -> list:
        """Generate population from UI configuration."""
        total_agents = config.get('total_agents', 100)
        
        if PopulationGenerator is None:
            print("PopulationGenerator not available, creating empty population")
            return []
        
        try:
            from src.population.distribution_config import DistributionConfig
            
            # Create a realistic default distribution configuration
            dist_config = DistributionConfig.create_realistic_default()
            generator = PopulationGenerator(dist_config)
            
            # Generate population - correct method signature
            population = generator.generate_population(size=total_agents)
            print(f"Generated population of {len(population)} agents")
            return population
        except Exception as e:
            print(f"Error generating population: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _create_metrics_collector(self, config: Dict[str, Any]) -> Optional['MetricsCollector']:
        """Create MetricsCollector based on data collection settings."""
        if MetricsCollector is None:
            return None
            
        data_collection = config.get('data_collection', {})
        
        try:
            return MetricsCollector()  # Adjust parameters as needed
        except Exception as e:
            print(f"Error creating metrics collector: {e}")
            return None
    
    def _extract_metrics_from_stats(self, month_stats) -> Dict[str, Any]:
        """Extract metrics from monthly statistics."""
        # Convert your MonthlyStats object to the format expected by the UI
        # This is a placeholder - adjust based on your actual MonthlyStats structure
        if hasattr(month_stats, '__dict__'):
            return {
                'employment_rate': getattr(month_stats, 'employment_rate', 0.8),
                'average_wealth': getattr(month_stats, 'average_wealth', 1000),
                'addiction_rate': getattr(month_stats, 'addiction_rate', 0.2),
                'homelessness_rate': getattr(month_stats, 'homelessness_rate', 0.1)
            }
        else:
            return {
                'employment_rate': 0.8,
                'average_wealth': 1000, 
                'addiction_rate': 0.2,
                'homelessness_rate': 0.1
            }
    
    def export_simulation_data(self, simulation_id: str, export_type: str, options: Dict[str, Any] = None) -> Optional[Path]:
        """Export simulation data in requested format."""
        if simulation_id not in self.active_simulations:
            return None
        
        simulation_data = self.active_simulations[simulation_id]
        
        try:
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create basic export file
            export_path = export_dir / f"{simulation_id}_{export_type}_{timestamp}.{export_type}"
            
            export_content = {
                'simulation_id': simulation_id,
                'config': simulation_data['config'],
                'status': simulation_data['status'],
                'created_at': simulation_data['created_at'].isoformat(),
                'export_type': export_type
            }
            
            if export_type == 'json':
                with open(export_path, 'w') as f:
                    json.dump(export_content, f, indent=2)
            elif export_type == 'csv':
                # Basic CSV export
                import csv
                with open(export_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Key', 'Value'])
                    for key, value in export_content.items():
                        writer.writerow([key, str(value)])
            
            print(f"Exported {export_type} data to {export_path}")
            return export_path
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None
    
    def _check_dependencies(self) -> bool:
        """Check if all required simulation components are available."""
        required_components = [City, Simulation, PopulationGenerator]
        available = all(component is not None for component in required_components)
        missing = [name for name, component in [
            ('City', City), ('Simulation', Simulation), ('PopulationGenerator', PopulationGenerator),
            ('MetricsCollector', MetricsCollector), ('DataExporter', DataExporter)
        ] if component is None]
        
        if missing:
            print(f"Missing components: {missing}")
        
        return available
    
    def list_active_simulations(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all active simulations with their status."""
        return {
            sim_id: {
                'id': sim_id,
                'status': sim_data['status'],
                'created_at': sim_data['created_at'].isoformat(),
                'config_name': sim_data['config'].get('city_name', 'Unnamed')
            }
            for sim_id, sim_data in self.active_simulations.items()
        } 