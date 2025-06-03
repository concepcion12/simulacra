"""
Type definitions and enums for the Simulacra simulation.
"""
from enum import Enum, auto
from typing import Dict, List, Set, Tuple, Optional, Any, NewType
from dataclasses import dataclass
import numpy as np

# Type aliases
AgentID = NewType('AgentID', str)
PlotID = NewType('PlotID', str)
DistrictID = NewType('DistrictID', str)
BuildingID = NewType('BuildingID', str)
EmployerID = NewType('EmployerID', str)
JobID = NewType('JobID', str)
UnitID = NewType('UnitID', str)

# Coordinate type for spatial locations
Coordinate = Tuple[float, float]


class ActionType(Enum):
    """Types of actions agents can take."""
    WORK = auto()
    BEG = auto()
    GAMBLE = auto()
    DRINK = auto()
    FIND_JOB = auto()
    FIND_HOUSING = auto()
    MOVE_HOME = auto()
    REST = auto()


class PlotType(Enum):
    """Types of plots in the city."""
    RESIDENTIAL_APARTMENT = auto()
    RESIDENTIAL_HOUSE = auto()
    LIQUOR_STORE = auto()
    CASINO = auto()
    EMPLOYER = auto()
    PUBLIC_SPACE = auto()
    VACANT = auto()


class DistrictWealth(Enum):
    """Wealth levels of districts."""
    POOR = auto()
    WORKING_CLASS = auto()
    MIDDLE_CLASS = auto()
    UPPER_CLASS = auto()


class SubstanceType(Enum):
    """Types of addictive substances."""
    ALCOHOL = auto()


class BehaviorType(Enum):
    """Types of habitual behaviors."""
    DRINKING = auto()
    GAMBLING = auto()


class CueType(Enum):
    """Types of environmental cues."""
    ALCOHOL_CUE = auto()
    GAMBLING_CUE = auto()
    FINANCIAL_STRESS_CUE = auto()


@dataclass
class ActionCost:
    """Time costs for different actions in hours."""
    WORK: float = 160.0          # Full-time monthly
    BEG: float = 8.0            # Per begging session
    GAMBLE: float = 4.0         # Per gambling session
    DRINK: float = 2.0          # Per drinking session
    FIND_JOB: float = 20.0      # Job searching
    FIND_HOUSING: float = 10.0  # House hunting
    MOVE_HOME: float = 20.0     # Moving process
    REST: float = 4.0           # Rest session


@dataclass
class PersonalityTraits:
    """Static personality traits for an agent."""
    baseline_impulsivity: float  # [0,1] affects β in hyperbolic discounting
    risk_preference_alpha: float  # gain curvature (prospect theory)
    risk_preference_beta: float   # loss curvature (prospect theory)
    risk_preference_lambda: float # loss aversion coefficient
    cognitive_type: float        # [0,1] θ parameter for dual-process
    addiction_vulnerability: float  # [0,1]
    gambling_bias_strength: float   # [0,1]


@dataclass
class InternalState:
    """Dynamic internal state of an agent."""
    mood: float = 0.0              # [-1,1] negative to positive
    stress: float = 0.0            # [0,1]
    cognitive_load: float = 0.0    # [0,1]
    self_control_resource: float = 1.0  # [0,1] depletes with use
    wealth: float = 1000.0         # Starting wealth
    monthly_expenses: float = 800.0  # Rent + basic needs


@dataclass
class AddictionState:
    """State of addiction for a substance."""
    stock: float = 0.0           # S_t addiction capital
    tolerance_level: float = 0.0
    withdrawal_severity: float = 0.0
    time_since_last_use: int = 0


@dataclass
class GamblingContext:
    """Context for gambling behavior and biases."""
    recent_outcomes: List['GamblingOutcome'] = None
    loss_streak: int = 0
    total_losses: float = 0.0
    total_wins: float = 0.0  # Track total winnings
    total_games: int = 0  # Track total number of gambling sessions
    
    def __post_init__(self):
        if self.recent_outcomes is None:
            self.recent_outcomes = []


@dataclass
class WorkPerformanceHistory:
    """Track work performance over time."""
    recent_performances: List[float] = None  # Last N performance scores
    average_performance: float = 1.0  # Running average
    months_employed: int = 0  # Total months at current job
    warnings_received: int = 0  # Performance warnings
    
    def __post_init__(self):
        if self.recent_performances is None:
            self.recent_performances = []
    
    def add_performance(self, performance: float) -> None:
        """Add a new performance score and update average."""
        self.recent_performances.append(performance)
        if len(self.recent_performances) > 12:  # Keep last 12 months
            self.recent_performances.pop(0)
        self.average_performance = sum(self.recent_performances) / len(self.recent_performances)
        
        # Track warnings for poor performance
        if performance < 0.5:
            self.warnings_received += 1


@dataclass
class EmploymentInfo:
    """Information about agent's employment."""
    employer_id: Optional[EmployerID] = None
    job_id: Optional[JobID] = None
    job_quality: float = 0.5  # [0,1] affects salary and conditions
    base_salary: float = 2000.0  # Monthly base salary
    performance_history: WorkPerformanceHistory = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = WorkPerformanceHistory()


@dataclass
class HousingInfo:
    """Information about agent's housing."""
    plot_id: Optional[PlotID] = None
    unit_id: Optional[UnitID] = None
    housing_quality: float = 0.5  # [0,1] affects mood and stress
    monthly_rent: float = 800.0
    months_at_residence: int = 0


@dataclass
class ActionBudget:
    """Monthly action budget management."""
    total_hours: float = 280.0
    spent_hours: float = 0.0
    
    def can_afford(self, hours: float) -> bool:
        """Check if agent can afford to spend hours on action."""
        return self.spent_hours + hours <= self.total_hours
    
    def spend(self, hours: float) -> None:
        """Spend hours from budget."""
        self.spent_hours += hours
    
    def reset(self) -> None:
        """Reset budget for new month."""
        self.spent_hours = 0.0
    
    @property
    def remaining_hours(self) -> float:
        """Get remaining hours in budget."""
        return self.total_hours - self.spent_hours


@dataclass
class EnvironmentalCue:
    """Base class for environmental cues."""
    intensity: float  # [0,1]
    source: Optional[PlotID] = None
    cue_type: CueType = None


@dataclass
class AlcoholCue(EnvironmentalCue):
    """Cue that triggers alcohol craving."""
    cue_type: CueType = CueType.ALCOHOL_CUE


@dataclass
class GamblingCue(EnvironmentalCue):
    """Cue that triggers gambling urge."""
    cue_type: CueType = CueType.GAMBLING_CUE


@dataclass
class FinancialStressCue(EnvironmentalCue):
    """Cue from financial pressure."""
    cue_type: CueType = CueType.FINANCIAL_STRESS_CUE


# Outcome types
@dataclass
class ActionOutcome:
    """Base class for action outcomes."""
    success: bool = True
    message: str = ""


@dataclass
class WorkOutcome(ActionOutcome):
    """Outcome from work action."""
    payment: float = 0.0
    performance: float = 1.0
    stress_increase: float = 0.0


@dataclass
class GamblingOutcome(ActionOutcome):
    """Outcome from gambling action."""
    monetary_change: float = 0.0
    was_near_miss: bool = False
    psychological_impact: float = 0.0


@dataclass
class DrinkingOutcome(ActionOutcome):
    """Outcome from drinking action."""
    cost: float = 0.0
    units_consumed: int = 0
    stress_relief: float = 0.0
    mood_change: float = 0.0


@dataclass
class BeggingOutcome(ActionOutcome):
    """Outcome from begging action."""
    income: float = 0.0
    social_cost: float = 0.0
    location_quality: float = 0.5  # Quality of begging location


@dataclass
class JobSearchOutcome(ActionOutcome):
    """Outcome from job search action."""
    job_found: bool = False
    job_quality: float = 0.0  # Salary and working conditions
    stress_change: float = 0.0


@dataclass
class HousingSearchOutcome(ActionOutcome):
    """Outcome from housing search action."""
    housing_found: bool = False
    housing_quality: float = 0.0
    rent_cost: float = 0.0


@dataclass
class MoveOutcome(ActionOutcome):
    """Outcome from moving to new housing."""
    move_cost: float = 0.0
    stress_change: float = 0.0
    new_location: Optional[PlotID] = None


@dataclass
class RestOutcome(ActionOutcome):
    """Outcome from resting action."""
    stress_reduction: float = 0.0
    mood_improvement: float = 0.0
    self_control_restoration: float = 0.0


@dataclass
class SimulationTime:
    """Simulation time tracking."""
    month: int = 1
    year: int = 1
    
    def advance(self) -> None:
        """Advance time by one month."""
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
    
    @property
    def total_months(self) -> int:
        """Get total months elapsed."""
        return (self.year - 1) * 12 + self.month
    
    @property
    def month_progress(self) -> float:
        """Get progress through current month [0,1]."""
        # This would be more sophisticated in real implementation
        return 0.5  # Placeholder


# Utility function component weights
@dataclass
class UtilityWeights:
    """Weights for different utility components."""
    financial: float = 0.3
    habit: float = 0.15
    addiction: float = 0.2
    psychological: float = 0.35
    
    def normalize(self) -> None:
        """Normalize weights to sum to 1."""
        total = (self.financial + self.habit + self.addiction + 
                self.psychological)
        if total > 0:
            self.financial /= total
            self.habit /= total
            self.addiction /= total
            self.psychological /= total 
