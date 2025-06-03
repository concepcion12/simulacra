"""
Plot system for Simulacra environment.
"""
from typing import Optional
from src.utils.types import PlotID, DistrictID, Coordinate, PlotType
from src.environment.spatial import euclidean_distance

class Plot:
    """Represents a spatial plot within the city."""
    def __init__(
        self,
        plot_id: PlotID,
        location: Coordinate,
        district: DistrictID,
        plot_type: PlotType,
        building: Optional[object] = None
    ):
        self.id = plot_id
        self.location = location
        self.district = district
        self.plot_type = plot_type
        self.building = building

    def get_distance_to(self, other: 'Plot') -> float:
        """Return Euclidean distance to another plot."""
        return euclidean_distance(self.location, other.location)

    def is_occupied(self) -> bool:
        """Check if the plot has a building."""
        return self.building is not None

    def __repr__(self) -> str:
        return (
            f"Plot(id={self.id}, type={self.plot_type.name}, "
            f"loc={self.location}, occupied={self.is_occupied()})"
        ) 