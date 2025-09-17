"""
Data streamer for real-time visualization.
Collects and formats simulation data for live dashboard updates.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from simulacra.agents.agent import Agent
from simulacra.simulation.simulation import Simulation
from simulacra.analytics.metrics import MetricsCollector
from simulacra.utils.types import Coordinate, SubstanceType


class DataStreamer:
    """
    Streams real-time simulation data for visualization.

    Collects and formats data for:
    - City map with agent locations
    - Agent state indicators
    - Building occupancy
    - Heat maps (stress, addiction, wealth)
    """

    def __init__(self, simulation: Simulation, metrics_collector: MetricsCollector):
        """
        Initialize data streamer.

        Args:
            simulation: The simulation instance to stream from
            metrics_collector: Metrics collector for population data
        """
        self.simulation = simulation
        self.metrics_collector = metrics_collector
        self.city = simulation.city

        # Per-round metrics history
        self.round_history: List[Dict[str, Any]] = []

        # Cache for efficient updates
        self._last_update_time: Optional[datetime] = None
        self._cached_city_layout: Optional[Dict[str, Any]] = None

    def get_city_layout_data(self) -> Dict[str, Any]:
        """
        Get static city layout data (buildings, districts, plots).
        This data doesn't change during simulation, so can be cached.

        Returns:
            Dictionary with city layout information
        """
        if self._cached_city_layout is None:
            self._cached_city_layout = self._build_city_layout()
        return self._cached_city_layout

    def get_realtime_data(self) -> Dict[str, Any]:
        """
        Get current real-time simulation data.

        Returns:
            Dictionary with all real-time data for visualization
        """
        current_time = datetime.now()

        # Get agent locations and states
        agent_data = self._get_agent_data()

        # Get building occupancy
        building_data = self._get_building_occupancy_data()

        # Collect per-round metrics
        round_metrics = self.metrics_collector.collect_round_metrics(
            self.simulation.agents,
            current_time
        )

        # Get population metrics
        population_metrics = self.metrics_collector.get_latest_population_metrics()

        # Get simulation state
        sim_state = self.simulation.get_simulation_state()

        data = {
            'timestamp': current_time.isoformat(),
            'simulation_state': sim_state,
            'agents': agent_data,
            'buildings': building_data,
            'population_metrics': population_metrics.to_dict() if population_metrics else None,
            'heat_map_data': self._get_heat_map_data(),
            'economic_indicators': self._get_economic_indicators(),
            'round_metrics': round_metrics.to_dict()
        }

        # Add to history
        self.round_history.append({
            'timestamp': current_time.isoformat(),
            'round': self.simulation.time_manager.current_round,
            'month': self.simulation.time_manager.current_time.month,
            'metrics': round_metrics.to_dict()
        })

        self._last_update_time = current_time
        return data

    def _build_city_layout(self) -> Dict[str, Any]:
        """Build static city layout data."""
        districts = []
        plots = []
        buildings = []

        for district in self.city.districts:
            districts.append({
                'id': district.id,
                'name': district.name,
                'wealth_level': district.wealth_level,
                'color': self._get_district_color(district.wealth_level)
            })

            for plot in district.plots:
                plots.append({
                    'id': plot.id,
                    'location': {'x': plot.location[0], 'y': plot.location[1]},
                    'district_id': plot.district,
                    'plot_type': (
                        plot.plot_type.name
                        if hasattr(plot.plot_type, 'name')
                        else str(plot.plot_type)
                    ),
                    'has_building': plot.is_occupied()
                })

                if plot.building:
                    building_info = {
                        'plot_id': plot.id,
                        'location': {'x': plot.location[0], 'y': plot.location[1]},
                        'type': type(plot.building).__name__,
                        'district_id': plot.district
                    }

                    # Add building-specific details
                    if hasattr(plot.building, 'capacity'):
                        building_info['capacity'] = plot.building.capacity
                    if hasattr(plot.building, 'quality'):
                        building_info['quality'] = plot.building.quality
                    if hasattr(plot.building, 'rent'):
                        building_info['rent'] = plot.building.rent
                    if hasattr(plot.building, 'salary'):
                        building_info['salary'] = plot.building.salary

                    buildings.append(building_info)

        return {
            'city_name': self.city.name,
            'districts': districts,
            'plots': plots,
            'buildings': buildings,
            'bounds': self._calculate_city_bounds()
        }

    def _get_agent_data(self) -> List[Dict[str, Any]]:
        """Get current agent locations and states."""
        agent_data = []

        for agent in self.simulation.agents:
            # Get agent location (current plot)
            location = getattr(agent, 'current_location', None)
            if location is None and hasattr(agent, 'home') and agent.home:
                location = self._get_building_location(agent.home)

            # Get latest metrics for this agent
            metrics = self.metrics_collector.get_agent_metrics(agent.id)

            agent_info = {
                'id': agent.id,
                'location': {
                    'x': location[0] if location else 0,
                    'y': location[1] if location else 0
                },
                'state': {
                    'wealth': agent.internal_state.wealth,
                    'stress': agent.internal_state.stress,
                    'mood': agent.internal_state.mood,
                    'self_control': agent.internal_state.self_control_resource,
                    'employed': agent.employment is not None,
                    'housed': agent.home is not None,
                    'addiction_level': self._get_alcohol_addiction_level(agent)
                },
                'visual_properties': {
                    'color': self._get_agent_color(agent),
                    'size': self._get_agent_size(agent),
                    'shape': self._get_agent_shape(agent)
                }
            }

            if metrics:
                agent_info['metrics'] = {
                    'action_diversity': metrics.action_diversity,
                    'most_frequent_action': metrics.most_frequent_action,
                    'action_success_rate': metrics.action_success_rate
                }

            agent_data.append(agent_info)

        return agent_data

    def _get_alcohol_addiction_level(self, agent: Agent) -> float:
        """Return the agent's alcohol addiction stock."""
        alcohol_state = agent.addiction_states.get(SubstanceType.ALCOHOL)
        if alcohol_state is None:
            return 0.0
        return alcohol_state.stock

    def _get_building_occupancy_data(self) -> List[Dict[str, Any]]:
        """Get building occupancy information."""
        building_data = []

        for district in self.city.districts:
            for plot in district.plots:
                if plot.building:
                    # Count occupants based on building type
                    occupancy_info = {
                        'plot_id': plot.id,
                        'building_type': type(plot.building).__name__,
                        'location': {'x': plot.location[0], 'y': plot.location[1]},
                        'occupancy': 0,
                        'capacity': getattr(plot.building, 'capacity', 1),
                        'occupancy_rate': 0.0
                    }

                    # Count current occupants
                    if hasattr(plot.building, 'current_occupants'):
                        occupancy_info['occupancy'] = len(plot.building.current_occupants)
                    elif hasattr(plot.building, 'residents'):
                        occupancy_info['occupancy'] = len(plot.building.residents)
                    else:
                        # Count agents at this location
                        occupancy_info['occupancy'] = sum(
                            1
                            for agent in self.simulation.agents
                            if self._agent_is_at_plot(agent, plot)
                        )

                    if occupancy_info['capacity'] > 0:
                        occupancy_info['occupancy_rate'] = (
                            occupancy_info['occupancy'] / occupancy_info['capacity']
                        )

                    building_data.append(occupancy_info)

        return building_data

    def _agent_is_at_plot(self, agent: Agent, plot) -> bool:
        """Determine whether an agent is associated with a plot."""
        if hasattr(agent, 'current_location') and agent.current_location == plot.location:
            return True
        if hasattr(agent, 'home') and agent.home == plot.building:
            return True
        return False

    def _get_heat_map_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate heat map data for stress, addiction, and wealth."""
        heat_maps = {
            'stress': [],
            'addiction': [],
            'wealth': []
        }

        # Group agents by location and calculate averages
        location_groups = {}
        for agent in self.simulation.agents:
            location = getattr(agent, 'current_location', None)
            if location is None and hasattr(agent, 'home') and agent.home:
                location = self._get_building_location(agent.home)

            if location:
                location_key = f"{location[0]},{location[1]}"
                if location_key not in location_groups:
                    location_groups[location_key] = []
                location_groups[location_key].append(agent)

        # Calculate averages for each location
        for location_key, agents in location_groups.items():
            x, y = map(float, location_key.split(','))

            if agents:
                avg_stress = (
                    sum(agent.internal_state.stress for agent in agents) / len(agents)
                )
                avg_addiction = (
                    sum(
                        self._get_alcohol_addiction_level(agent)
                        for agent in agents
                    )
                    / len(agents)
                )
                avg_wealth = (
                    sum(agent.internal_state.wealth for agent in agents) / len(agents)
                )

                heat_maps['stress'].append({
                    'x': x, 'y': y, 'value': avg_stress, 'count': len(agents)
                })
                heat_maps['addiction'].append({
                    'x': x, 'y': y, 'value': avg_addiction, 'count': len(agents)
                })
                heat_maps['wealth'].append({
                    'x': x, 'y': y, 'value': avg_wealth, 'count': len(agents)
                })

        return heat_maps

    def _get_economic_indicators(self) -> Dict[str, Any]:
        """Get current economic indicators."""
        try:
            economic_summary = self.city.global_economy.get_economic_summary()
            return economic_summary
        except Exception:  # pragma: no cover - dependent on optional subsystems
            return {}

    def _calculate_city_bounds(self) -> Dict[str, float]:
        """Calculate the bounding box of the city."""
        if not self.city.districts:
            return {'min_x': 0, 'max_x': 100, 'min_y': 0, 'max_y': 100}

        all_plots = []
        for district in self.city.districts:
            all_plots.extend(district.plots)

        if not all_plots:
            return {'min_x': 0, 'max_x': 100, 'min_y': 0, 'max_y': 100}

        x_coords = [plot.location[0] for plot in all_plots]
        y_coords = [plot.location[1] for plot in all_plots]

        return {
            'min_x': min(x_coords),
            'max_x': max(x_coords),
            'min_y': min(y_coords),
            'max_y': max(y_coords)
        }

    def _get_building_location(self, building) -> Optional[Coordinate]:
        """Get the location of a building."""
        for district in self.city.districts:
            for plot in district.plots:
                if plot.building == building:
                    return plot.location
        return None

    def _get_district_color(self, wealth_level: int) -> str:
        """Get color for district based on wealth level."""
        colors = {
            1: '#8B0000',  # Dark red for poor
            2: '#CD5C5C',  # Indian red for lower-middle
            3: '#32CD32',  # Lime green for middle
            4: '#4169E1',  # Royal blue for upper-middle
            5: '#FFD700'   # Gold for wealthy
        }
        return colors.get(wealth_level, '#808080')

    def _get_agent_color(self, agent: Agent) -> str:
        """Get color for agent based on their state."""
        # Color by stress level
        stress = agent.internal_state.stress
        if stress > 0.8:
            return '#FF0000'  # Red for high stress
        elif stress > 0.5:
            return '#FFA500'  # Orange for medium stress
        else:
            return '#00FF00'  # Green for low stress

    def _get_agent_size(self, agent: Agent) -> float:
        """Get size for agent based on wealth."""
        wealth = agent.internal_state.wealth
        # Normalize to reasonable size range (3-12 pixels)
        return max(3, min(12, 3 + (wealth / 1000) * 9))

    def _get_agent_shape(self, agent: Agent) -> str:
        """Get shape for agent based on employment status."""
        if agent.employment is not None:
            return 'circle'  # Employed
        else:
            return 'square'  # Unemployed

    def get_round_history(self) -> List[Dict[str, Any]]:
        """Return the collected per-round metrics history."""
        return self.round_history
