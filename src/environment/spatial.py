"""
Spatial utilities for Simulacra environment.
"""
import math
from typing import List
from src.utils.types import Coordinate


def euclidean_distance(a: Coordinate, b: Coordinate) -> float:
    """Compute Euclidean distance between two coordinates."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def manhattan_distance(a: Coordinate, b: Coordinate) -> float:
    """Compute Manhattan distance between two coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def within_euclidean_radius(
    center: Coordinate,
    points: List[Coordinate],
    radius: float
) -> List[Coordinate]:
    """
    Return points within a given Euclidean radius of center.
    """
    return [p for p in points if euclidean_distance(center, p) <= radius]


def within_manhattan_radius(
    center: Coordinate,
    points: List[Coordinate],
    radius: float
) -> List[Coordinate]:
    """
    Return points within a given Manhattan radius of center.
    """
    return [p for p in points if manhattan_distance(center, p) <= radius] 
