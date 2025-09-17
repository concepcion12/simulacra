"""City core for Simulacra environment."""
from typing import List, Dict, Optional, Type, Any, TYPE_CHECKING
from simulacra.utils.types import PlotID, DistrictID, Coordinate, SimulationTime
from simulacra.environment.plot import Plot
from simulacra.environment.district import District
from simulacra.environment.spatial import euclidean_distance

if TYPE_CHECKING:
    from simulacra.simulation.economy import EconomyManager


class City:
    """Represents the city containing districts, plots, and buildings."""
    def __init__(
        self,
        name: str,
        districts: List[District],
        time: Optional[SimulationTime] = None,
        global_economy: Optional['EconomyManager'] = None
    ):
        self.name = name
        self.districts = districts
        self.time = time or SimulationTime()

        # Create economy manager if not provided
        if global_economy is None:
            # Import here to avoid circular import
            from simulacra.simulation.economy import EconomyManager
            self.global_economy = EconomyManager()
        else:
            self.global_economy = global_economy

        # Build plot index for fast lookup
        self._plot_index: Dict[PlotID, Plot] = {}
        for district in self.districts:
            for plot in district.plots:
                self._plot_index[plot.id] = plot

    def get_plot(self, plot_id: PlotID) -> Optional[Plot]:
        """Retrieve a plot by its ID."""
        return self._plot_index.get(plot_id)

    def get_district(self, district_id: DistrictID) -> Optional[District]:
        """Retrieve a district by its ID."""
        for d in self.districts:
            if d.id == district_id:
                return d
        return None

    def get_nearby_buildings(
        self,
        location: Coordinate,
        building_class: Type,
        radius: float
    ) -> List[Any]:
        """
        Return all buildings of a given class within a radius of location.
        """
        result = []
        for plot in self._plot_index.values():
            building = getattr(plot, 'building', None)
            if building and isinstance(building, building_class):
                if euclidean_distance(location, plot.location) <= radius:
                    result.append(building)
        return result

    def __repr__(self) -> str:
        return f"City(name={self.name}, districts={len(self.districts)})"
