"""
District structure for Simulacra environment.
"""
from typing import List
from src.utils.types import DistrictID, PlotType, Coordinate, DistrictWealth
from src.environment.plot import Plot
from src.environment.spatial import euclidean_distance

class District:
    """Represents a district containing multiple plots."""
    def __init__(
        self,
        district_id: DistrictID | None = None,
        name: str | None = None,
        wealth_level: DistrictWealth | None = None,
        plots: List[Plot] | None = None,
        base_rent_modifier: float = 1.0,
        crime_rate: float = 0.0,
        **kwargs,
    ):
        if district_id is None:
            district_id = kwargs.get("id")

        self.id = district_id
        self.name = name
        self.wealth_level = wealth_level
        self.plots = plots if plots is not None else []
        self.base_rent_modifier = base_rent_modifier
        self.crime_rate = crime_rate

    def get_available_plots(self, plot_type: PlotType) -> List[Plot]:
        """Return all plots of a given type."""
        return [p for p in self.plots if p.plot_type == plot_type]

    def get_nearby_plots(
        self,
        center: Coordinate,
        radius: float
    ) -> List[Plot]:
        """Return plots within a given radius of a coordinate."""
        return [p for p in self.plots
                if euclidean_distance(p.location, center) <= radius]

    def __repr__(self) -> str:
        return (
            f"District(id={self.id}, name={self.name}, "
            f"wealth={self.wealth_level.name}, plots={len(self.plots)})"
        ) 
