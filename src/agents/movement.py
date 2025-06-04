"""
Movement system for agents in the Simulacra simulation.

Handles:
- Agent movement between plots
- Time costs for movement based on distance
- Location-based action availability
"""
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass

from src.utils.types import (
    PlotID, ActionType, BuildingID
)
from src.environment.spatial import euclidean_distance
from src.environment.plot import Plot
from src.environment.city import City
from src.environment.buildings.liquor_store import LiquorStore
from src.environment.buildings.casino import Casino
from src.environment.buildings.employer import Employer
from src.environment.buildings.public_space import PublicSpace
from src.environment.buildings.residential import ResidentialBuilding


@dataclass
class MovementCost:
    """Movement cost configuration."""
    # Base walking speed in plots per hour
    base_speed: float = 2.0
    # Minimum time cost for any movement (in hours)
    minimum_time: float = 0.5
    # Fatigue multiplier based on stress
    fatigue_multiplier: float = 0.2


class MovementSystem:
    """Manages agent movement and location-based constraints."""
    
    def __init__(self, city: City, movement_cost: MovementCost = None):
        """
        Initialize movement system.
        
        Args:
            city: The city containing all plots and buildings
            movement_cost: Configuration for movement costs
        """
        self.city = city
        self.movement_cost = movement_cost or MovementCost()
        
        # Cache action-to-building mappings
        self.action_building_map = {
            ActionType.WORK: Employer,
            ActionType.DRINK: LiquorStore,
            ActionType.GAMBLE: Casino,
            ActionType.BEG: PublicSpace,
            ActionType.FIND_HOUSING: ResidentialBuilding,
        }
    
    def calculate_movement_time(
        self, 
        from_plot: PlotID, 
        to_plot: PlotID,
        agent_stress: float = 0.0
    ) -> float:
        """
        Calculate time cost to move between plots.
        
        Args:
            from_plot: Starting plot ID
            to_plot: Destination plot ID
            agent_stress: Agent's current stress level (affects movement speed)
            
        Returns:
            Time cost in hours
        """
        # Get plot objects
        start = self.city.get_plot(from_plot)
        end = self.city.get_plot(to_plot)
        
        if not start or not end:
            raise ValueError(f"Invalid plot IDs: {from_plot} or {to_plot}")
        
        # Same plot = no movement needed
        if from_plot == to_plot:
            return 0.0
        
        # Calculate distance
        distance = euclidean_distance(start.location, end.location)
        
        # Base time = distance / speed
        base_time = distance / self.movement_cost.base_speed
        
        # Apply stress fatigue (stressed agents move slower)
        fatigue_factor = 1.0 + (agent_stress * self.movement_cost.fatigue_multiplier)
        actual_time = base_time * fatigue_factor
        
        # Apply minimum time
        return max(self.movement_cost.minimum_time, actual_time)
    
    def get_plots_within_time_budget(
        self,
        from_plot: PlotID,
        time_budget: float,
        agent_stress: float = 0.0
    ) -> Set[PlotID]:
        """
        Get all plots reachable within a time budget.
        
        Args:
            from_plot: Starting plot ID
            time_budget: Available time in hours
            agent_stress: Agent's current stress level
            
        Returns:
            Set of reachable plot IDs
        """
        reachable = set()
        
        for plot_id in self.city._plot_index:
            time_cost = self.calculate_movement_time(
                from_plot, plot_id, agent_stress
            )
            if time_cost <= time_budget:
                reachable.add(plot_id)
        
        return reachable
    
    def find_nearest_building(
        self,
        from_plot: PlotID,
        building_type: type,
        max_distance: Optional[float] = None
    ) -> Optional[Tuple[BuildingID, PlotID, float]]:
        """
        Find the nearest building of a specific type.
        
        Args:
            from_plot: Starting plot ID
            building_type: Type of building to find
            max_distance: Maximum distance to search (None = unlimited)
            
        Returns:
            Tuple of (building_id, plot_id, distance) or None if not found
        """
        start_plot = self.city.get_plot(from_plot)
        if not start_plot:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for plot_id, plot in self.city._plot_index.items():
            if plot.building and isinstance(plot.building, building_type):
                distance = euclidean_distance(start_plot.location, plot.location)
                
                if max_distance and distance > max_distance:
                    continue
                    
                if distance < min_distance:
                    min_distance = distance
                    nearest = (plot.building.id, plot_id, distance)
        
        return nearest
    
    def get_available_action_targets(
        self,
        agent_location: PlotID,
        action_type: ActionType,
        time_budget: float,
        agent_stress: float = 0.0
    ) -> List[Tuple[BuildingID, PlotID, float]]:
        """
        Get all available targets for a specific action type within time budget.
        
        Args:
            agent_location: Agent's current location
            action_type: Type of action to perform
            time_budget: Available time in hours
            agent_stress: Agent's current stress level
            
        Returns:
            List of tuples (building_id, plot_id, travel_time)
        """
        # Special cases that don't require specific buildings
        if action_type in [ActionType.REST, ActionType.MOVE_HOME]:
            return []
        
        # Get required building type
        building_type = self.action_building_map.get(action_type)
        if not building_type:
            return []
        
        # Get reachable plots
        reachable_plots = self.get_plots_within_time_budget(
            agent_location, time_budget, agent_stress
        )
        
        # Find all buildings of the required type in reachable plots
        targets = []
        for plot_id in reachable_plots:
            plot = self.city.get_plot(plot_id)
            if plot and plot.building and isinstance(plot.building, building_type):
                travel_time = self.calculate_movement_time(
                    agent_location, plot_id, agent_stress
                )
                targets.append((plot.building.id, plot_id, travel_time))
        
        # Sort by travel time (nearest first)
        targets.sort(key=lambda x: x[2])
        
        return targets
    
    def can_perform_action_at_location(
        self,
        action_type: ActionType,
        agent_location: PlotID,
        target_location: Optional[PlotID] = None
    ) -> bool:
        """
        Check if an action can be performed at a location.
        
        Args:
            action_type: Type of action to check
            agent_location: Agent's current location
            target_location: Target location (if different from current)
            
        Returns:
            Whether the action can be performed
        """
        # Actions that can be done anywhere
        if action_type == ActionType.REST:
            return True
        
        # Actions that require being at home
        if action_type in [ActionType.MOVE_HOME]:
            return True  # Can always attempt to go home
        
        # Check if at target location or current location has required building
        check_location = target_location or agent_location
        plot = self.city.get_plot(check_location)
        
        if not plot or not plot.building:
            return False
        
        # Check building type matches action requirement
        required_type = self.action_building_map.get(action_type)
        if required_type:
            return isinstance(plot.building, required_type)
        
        return False
    
    def get_movement_options(
        self,
        agent_location: PlotID,
        time_budget: float,
        agent_stress: float = 0.0,
        important_locations: Optional[Dict[str, PlotID]] = None
    ) -> List[Tuple[PlotID, float, str]]:
        """
        Get movement options for an agent.
        
        Args:
            agent_location: Agent's current location
            time_budget: Available time in hours
            agent_stress: Agent's current stress level
            important_locations: Dict of important locations (e.g., 'home', 'work')
            
        Returns:
            List of tuples (plot_id, travel_time, description)
        """
        options = []
        
        # Add important locations if provided
        if important_locations:
            for desc, plot_id in important_locations.items():
                if plot_id and plot_id != agent_location:
                    travel_time = self.calculate_movement_time(
                        agent_location, plot_id, agent_stress
                    )
                    if travel_time <= time_budget:
                        options.append((plot_id, travel_time, f"Move to {desc}"))
        
        # Add nearby points of interest
        reachable = self.get_plots_within_time_budget(
            agent_location, time_budget, agent_stress
        )
        
        for plot_id in reachable:
            if plot_id == agent_location:
                continue
                
            plot = self.city.get_plot(plot_id)
            if plot and plot.building:
                travel_time = self.calculate_movement_time(
                    agent_location, plot_id, agent_stress
                )
                
                # Create description based on building type
                building_desc = type(plot.building).__name__
                options.append((plot_id, travel_time, f"Move to {building_desc}"))
        
        # Sort by travel time
        options.sort(key=lambda x: x[1])
        
        return options 
