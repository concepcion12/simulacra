"""Tests for the Plot class in the environment module."""
from simulacra.environment.plot import Plot
from simulacra.utils.types import PlotID, DistrictID, Coordinate, PlotType


def test_plot_repr_handles_missing_optional_fields() -> None:
    """Ensure __repr__ does not raise when optional data is absent."""
    plot = Plot()

    result = repr(plot)

    assert "type=UNKNOWN" in result
    assert "occupied=False" in result


def test_plot_repr_includes_provided_information() -> None:
    """The representation should include provided identifiers and location."""
    plot = Plot(
        plot_id=PlotID("plot-1"),
        location=Coordinate((1.0, 2.0)),
        district=DistrictID("district-1"),
        plot_type=PlotType.PUBLIC_SPACE,
    )

    result = repr(plot)

    assert "Plot(id=plot-1" in result
    assert "type=PUBLIC_SPACE" in result
    assert "loc=(1.0, 2.0)" in result
