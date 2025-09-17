"""
Distribution configuration system for population generation.

Provides flexible ways to specify probability distributions for all agent attributes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum
import numpy as np
import json


class DistributionType(Enum):
    """Types of probability distributions supported."""
    NORMAL = "normal"
    UNIFORM = "uniform"
    BETA = "beta"
    LOGNORMAL = "lognormal"
    CATEGORICAL = "categorical"
    FIXED = "fixed"
    BIMODAL = "bimodal"


@dataclass
class DistributionSpec:
    """Specification for a single attribute distribution."""
    dist_type: DistributionType
    params: Dict[str, Any]
    bounds: Optional[Tuple[float, float]] = None  # (min, max) clipping
    description: str = ""

    def sample(self, size: int = 1) -> Union[float, np.ndarray]:
        """Sample from this distribution."""
        if self.dist_type == DistributionType.NORMAL:
            mean = self.params.get('mean', 0.0)
            std = self.params.get('std', 1.0)
            values = np.random.normal(mean, std, size)

        elif self.dist_type == DistributionType.UNIFORM:
            low = self.params.get('low', 0.0)
            high = self.params.get('high', 1.0)
            values = np.random.uniform(low, high, size)

        elif self.dist_type == DistributionType.BETA:
            alpha = self.params.get('alpha', 2.0)
            beta = self.params.get('beta', 2.0)
            values = np.random.beta(alpha, beta, size)

        elif self.dist_type == DistributionType.LOGNORMAL:
            mean = self.params.get('mean', 0.0)
            sigma = self.params.get('sigma', 1.0)
            values = np.random.lognormal(mean, sigma, size)

        elif self.dist_type == DistributionType.CATEGORICAL:
            categories = self.params.get('categories', [])
            probabilities = self.params.get('probabilities', None)
            values = np.random.choice(categories, size, p=probabilities)

        elif self.dist_type == DistributionType.FIXED:
            value = self.params.get('value', 0.0)
            values = np.full(size, value)

        elif self.dist_type == DistributionType.BIMODAL:
            # Two normal distributions mixed
            mean1 = self.params.get('mean1', -1.0)
            std1 = self.params.get('std1', 0.5)
            mean2 = self.params.get('mean2', 1.0)
            std2 = self.params.get('std2', 0.5)
            weight1 = self.params.get('weight1', 0.5)

            # Sample from mixture
            component = np.random.random(size) < weight1
            values = np.where(
                component,
                np.random.normal(mean1, std1, size),
                np.random.normal(mean2, std2, size)
            )
        else:
            raise ValueError(f"Unknown distribution type: {self.dist_type}")

        # Apply bounds if specified
        if self.bounds is not None:
            values = np.clip(values, self.bounds[0], self.bounds[1])

        return values[0] if size == 1 else values


@dataclass
class DistributionConfig:
    """Complete configuration for population attribute distributions."""

    # Personality trait distributions
    personality_traits: Dict[str, DistributionSpec] = field(default_factory=dict)

    # Economic distributions
    initial_wealth: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.LOGNORMAL,
            {'mean': 7.0, 'sigma': 0.8},  # ~1000 median with spread
            bounds=(100, 50000),
            description="Initial wealth distribution"
        )
    )

    monthly_expenses: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.NORMAL,
            {'mean': 800, 'std': 200},
            bounds=(400, 2000),
            description="Monthly living expenses"
        )
    )

    # Initial internal state distributions
    initial_mood: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.NORMAL,
            {'mean': 0.0, 'std': 0.3},
            bounds=(-1.0, 1.0),
            description="Starting mood"
        )
    )

    initial_stress: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.BETA,
            {'alpha': 2.0, 'beta': 3.0},  # Slightly skewed toward lower stress
            bounds=(0.0, 1.0),
            description="Starting stress level"
        )
    )

    initial_self_control: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.BETA,
            {'alpha': 3.0, 'beta': 2.0},  # Slightly skewed toward higher self-control
            bounds=(0.2, 1.0),  # Everyone starts with some self-control
            description="Starting self-control resources"
        )
    )

    # Initial behavioral state distributions
    initial_drinking_habit: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.BETA,
            {'alpha': 1.0, 'beta': 4.0},  # Most start with low drinking habits
            bounds=(0.0, 0.5),  # Cap initial habits
            description="Starting drinking habit strength"
        )
    )

    initial_gambling_habit: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.BETA,
            {'alpha': 1.0, 'beta': 9.0},  # Very few start with gambling habits
            bounds=(0.0, 0.3),
            description="Starting gambling habit strength"
        )
    )

    initial_addiction_stock: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.BETA,
            {'alpha': 1.0, 'beta': 9.0},  # Most start with no addiction
            bounds=(0.0, 0.2),  # Small initial addiction stock possible
            description="Starting addiction capital"
        )
    )

    # Demographic distributions
    name_categories: DistributionSpec = field(
        default_factory=lambda: DistributionSpec(
            DistributionType.CATEGORICAL,
            {
                'categories': [
                    'Alex', 'Jordan', 'Taylor', 'Casey', 'Riley', 'Morgan', 'Blake', 'Jamie',
                    'Avery', 'Quinn', 'Sage', 'Drew', 'Cameron', 'Emery', 'Finley', 'Hayden',
                    'Peyton', 'Reese', 'Rowan', 'Skyler', 'Parker', 'Dakota', 'Kendall', 'River'
                ]
            },
            description="Name selection"
        )
    )

    def __post_init__(self):
        """Initialize default personality trait distributions if not provided."""
        if not self.personality_traits:
            self.personality_traits = self._create_default_personality_distributions()

    def _create_default_personality_distributions(self) -> Dict[str, DistributionSpec]:
        """Create realistic default distributions for personality traits."""
        return {
            'baseline_impulsivity': DistributionSpec(
                DistributionType.BETA,
                {'alpha': 2.0, 'beta': 2.0},  # Symmetric around 0.5
                bounds=(0.0, 1.0),
                description="Baseline impulsivity (affects temporal discounting)"
            ),

            'risk_preference_alpha': DistributionSpec(
                DistributionType.NORMAL,
                {'mean': 0.88, 'std': 0.1},  # Literature standard
                bounds=(0.5, 1.0),
                description="Gain curvature in prospect theory"
            ),

            'risk_preference_beta': DistributionSpec(
                DistributionType.NORMAL,
                {'mean': 0.88, 'std': 0.1},
                bounds=(0.5, 1.0),
                description="Loss curvature in prospect theory"
            ),

            'risk_preference_lambda': DistributionSpec(
                DistributionType.NORMAL,
                {'mean': 2.25, 'std': 0.5},  # Loss aversion coefficient
                bounds=(1.0, 4.0),
                description="Loss aversion strength"
            ),

            'cognitive_type': DistributionSpec(
                DistributionType.BETA,
                {'alpha': 3.0, 'beta': 2.0},  # Slightly more System 2 thinkers
                bounds=(0.0, 1.0),
                description="Dual-process thinking style (0=System 1, 1=System 2)"
            ),

            'addiction_vulnerability': DistributionSpec(
                DistributionType.BETA,
                {'alpha': 2.0, 'beta': 5.0},  # Most people have low vulnerability
                bounds=(0.0, 1.0),
                description="Vulnerability to developing addictions"
            ),

            'gambling_bias_strength': DistributionSpec(
                DistributionType.BETA,
                {'alpha': 2.0, 'beta': 3.0},  # Moderate gambling bias
                bounds=(0.0, 1.0),
                description="Strength of gambling-related cognitive biases"
            )
        }

    @classmethod
    def create_realistic_default(cls) -> 'DistributionConfig':
        """Create a configuration with realistic population distributions."""
        return cls()

    @classmethod
    def create_diverse_population(cls) -> 'DistributionConfig':
        """Create a configuration for maximum population diversity."""
        config = cls()

        # Make personality traits more diverse
        config.personality_traits['baseline_impulsivity'] = DistributionSpec(
            DistributionType.UNIFORM, {'low': 0.0, 'high': 1.0},
            description="Uniform impulsivity for maximum diversity"
        )

        config.personality_traits['cognitive_type'] = DistributionSpec(
            DistributionType.UNIFORM, {'low': 0.0, 'high': 1.0},
            description="Uniform cognitive type distribution"
        )

        # More diverse wealth distribution
        config.initial_wealth = DistributionSpec(
            DistributionType.BIMODAL,
            {'mean1': 6.5, 'std1': 0.3, 'mean2': 8.5, 'std2': 0.5, 'weight1': 0.7},
            bounds=(50, 100000),
            description="Bimodal wealth (working class + upper middle class)"
        )

        return config

    @classmethod
    def create_vulnerable_population(cls) -> 'DistributionConfig':
        """Create a configuration focused on addiction-vulnerable individuals."""
        config = cls()

        # Higher impulsivity
        config.personality_traits['baseline_impulsivity'] = DistributionSpec(
            DistributionType.BETA, {'alpha': 3.0, 'beta': 2.0},
            bounds=(0.2, 1.0),
            description="Higher impulsivity population"
        )

        # Higher addiction vulnerability
        config.personality_traits['addiction_vulnerability'] = DistributionSpec(
            DistributionType.BETA, {'alpha': 3.0, 'beta': 2.0},
            bounds=(0.1, 1.0),
            description="High addiction vulnerability"
        )

        # More financial stress
        config.initial_wealth = DistributionSpec(
            DistributionType.LOGNORMAL, {'mean': 6.0, 'sigma': 0.8},
            bounds=(50, 10000),
            description="Lower initial wealth"
        )

        # Higher initial stress
        config.initial_stress = DistributionSpec(
            DistributionType.BETA, {'alpha': 3.0, 'beta': 2.0},
            bounds=(0.2, 1.0),
            description="Higher initial stress levels"
        )

        return config

    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        # Convert to serializable format
        config_dict = {}

        # Handle personality traits
        config_dict['personality_traits'] = {}
        for name, spec in self.personality_traits.items():
            config_dict['personality_traits'][name] = {
                'dist_type': spec.dist_type.value,
                'params': spec.params,
                'bounds': spec.bounds,
                'description': spec.description
            }

        # Handle other distributions
        for attr_name in ['initial_wealth', 'monthly_expenses', 'initial_mood',
                         'initial_stress', 'initial_self_control', 'initial_drinking_habit',
                         'initial_gambling_habit', 'initial_addiction_stock', 'name_categories']:
            spec = getattr(self, attr_name)
            config_dict[attr_name] = {
                'dist_type': spec.dist_type.value,
                'params': spec.params,
                'bounds': spec.bounds,
                'description': spec.description
            }

        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'DistributionConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)

        config = cls.__new__(cls)  # Create without calling __init__

        # Load personality traits
        config.personality_traits = {}
        for name, spec_dict in config_dict.get('personality_traits', {}).items():
            config.personality_traits[name] = DistributionSpec(
                DistributionType(spec_dict['dist_type']),
                spec_dict['params'],
                tuple(spec_dict['bounds']) if spec_dict['bounds'] else None,
                spec_dict.get('description', '')
            )

        # Load other distributions
        for attr_name in ['initial_wealth', 'monthly_expenses', 'initial_mood',
                         'initial_stress', 'initial_self_control', 'initial_drinking_habit',
                         'initial_gambling_habit', 'initial_addiction_stock', 'name_categories']:
            if attr_name in config_dict:
                spec_dict = config_dict[attr_name]
                setattr(config, attr_name, DistributionSpec(
                    DistributionType(spec_dict['dist_type']),
                    spec_dict['params'],
                    tuple(spec_dict['bounds']) if spec_dict['bounds'] else None,
                    spec_dict.get('description', '')
                ))

        return config

    def update_personality_trait(self, trait_name: str, dist_spec: DistributionSpec) -> None:
        """Update a specific personality trait distribution."""
        self.personality_traits[trait_name] = dist_spec

    def update_economic_distribution(self, wealth_dist: DistributionSpec,
                                   expense_dist: Optional[DistributionSpec] = None) -> None:
        """Update economic distributions."""
        self.initial_wealth = wealth_dist
        if expense_dist:
            self.monthly_expenses = expense_dist

    def get_summary(self) -> Dict[str, str]:
        """Get a summary of all distributions for review."""
        summary = {}

        summary['Personality Traits'] = {
            name: f"{spec.dist_type.value}({spec.params}) bounds={spec.bounds}"
            for name, spec in self.personality_traits.items()
        }

        for attr_name in ['initial_wealth', 'monthly_expenses', 'initial_mood',
                         'initial_stress', 'initial_self_control']:
            spec = getattr(self, attr_name)
            summary[attr_name] = f"{spec.dist_type.value}({spec.params}) bounds={spec.bounds}"

        return summary
