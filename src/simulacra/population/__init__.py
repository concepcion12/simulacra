"""
Population generation and management system for Simulacra.

This module provides tools for generating diverse agent populations with
configurable attribute distributions, reviewing generated populations,
and adjusting population parameters.
"""

from .distribution_config import DistributionConfig, DistributionType, DistributionSpec
from .population_generator import PopulationGenerator, QuickPopulationFactory
from .population_analyzer import PopulationAnalyzer, PopulationStats

__all__ = [
    'DistributionConfig',
    'DistributionType', 
    'DistributionSpec',
    'PopulationGenerator',
    'QuickPopulationFactory',
    'PopulationAnalyzer',
    'PopulationStats'
] 
