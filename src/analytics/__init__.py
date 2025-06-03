"""
Analytics package for Simulacra simulation data collection and analysis.

This package implements Phase 7.1-7.3 of the roadmap:
- Metrics System (7.1): Agent-level and population-level metrics tracking
- History Tracking (7.2): Detailed event and state history logging  
- Export Capabilities (7.3): CSV, JSON, and statistical report exports
"""

from .metrics import (
    AgentMetrics, PopulationMetrics, MetricsCollector,
    BehavioralPattern, EconomicIndicators
)
from .history import (
    HistoryTracker, AgentHistory, LifeEvent, StateSnapshot,
    ActionRecord, EventType
)
from .exporters import (
    DataExporter, CSVExporter, JSONExporter, StatisticalReporter
)

__all__ = [
    # Metrics System
    "AgentMetrics",
    "PopulationMetrics", 
    "MetricsCollector",
    "BehavioralPattern",
    "EconomicIndicators",
    
    # History Tracking
    "HistoryTracker",
    "AgentHistory",
    "LifeEvent",
    "StateSnapshot",
    "ActionRecord", 
    "EventType",
    
    # Export Capabilities
    "DataExporter",
    "CSVExporter",
    "JSONExporter",
    "StatisticalReporter"
] 