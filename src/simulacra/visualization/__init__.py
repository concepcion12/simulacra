"""
Real-time visualization system for Simulacra.
Implements Phase 8.1: Real-time Visualization and Unified Interface.
"""

from .real_time_dashboard import RealtimeDashboard
from .data_streamer import DataStreamer
from .visualization_server import VisualizationServer
from .configuration import SimulationConfiguration
from .project_management import ProjectManager, Project
from .template_library import TemplateManager
from .simulation_control import SimulationManager
from .unified_app import UnifiedSimulacraApp

__all__ = [
    'RealtimeDashboard',
    'DataStreamer',
    'VisualizationServer',
    'UnifiedSimulacraApp',
    'ProjectManager',
    'SimulationConfiguration',
    'TemplateManager',
    'SimulationManager',
    'Project'
]
