"""
Population generator for creating diverse agent populations.

Uses DistributionConfig to generate agents with varied characteristics
according to specified probability distributions.
"""

import uuid
from typing import List, Optional, Dict, Any
import numpy as np
from dataclasses import dataclass

from src.agents.agent import Agent
from src.utils.types import (
    AgentID, PersonalityTraits,
    BehaviorType, SubstanceType, PlotID
)
from .distribution_config import DistributionConfig


@dataclass
class PopulationSeed:
    """Seed data for reproducible population generation."""
    numpy_seed: int
    personality_seeds: Dict[str, int]
    economic_seed: int
    behavioral_seed: int
    demographic_seed: int


class PopulationGenerator:
    """Generates diverse agent populations according to distribution specifications."""
    
    def __init__(self, config: DistributionConfig, seed: Optional[int] = None):
        """
        Initialize population generator.
        
        Args:
            config: Distribution configuration for agent attributes
            seed: Random seed for reproducible generation
        """
        self.config = config
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Track generation statistics
        self.generation_stats = {
            'total_generated': 0,
            'generation_time': 0.0,
            'attribute_ranges': {}
        }
    
    def generate_population(
        self, 
        size: int, 
        starting_locations: Optional[List[PlotID]] = None,
        name_prefix: Optional[str] = None
    ) -> List[Agent]:
        """
        Generate a population of agents.
        
        Args:
            size: Number of agents to generate
            starting_locations: Optional list of starting locations (cycled through)
            name_prefix: Optional prefix for agent names
            
        Returns:
            List of generated agents
        """
        agents = []
        
        # Pre-generate all attributes for efficiency
        personality_data = self._generate_personality_traits(size)
        economic_data = self._generate_economic_attributes(size)
        state_data = self._generate_initial_states(size)
        behavioral_data = self._generate_behavioral_states(size)
        demographic_data = self._generate_demographic_attributes(size, name_prefix)
        
        # Create agents
        for i in range(size):
            # Determine location
            location = None
            if starting_locations:
                location = starting_locations[i % len(starting_locations)]
            
            # Create personality traits
            personality = PersonalityTraits(
                baseline_impulsivity=personality_data['baseline_impulsivity'][i],
                risk_preference_alpha=personality_data['risk_preference_alpha'][i],
                risk_preference_beta=personality_data['risk_preference_beta'][i],
                risk_preference_lambda=personality_data['risk_preference_lambda'][i],
                cognitive_type=personality_data['cognitive_type'][i],
                addiction_vulnerability=personality_data['addiction_vulnerability'][i],
                gambling_bias_strength=personality_data['gambling_bias_strength'][i]
            )
            
            # Create agent with basic parameters
            agent = Agent(
                agent_id=AgentID(str(uuid.uuid4())),
                name=demographic_data['names'][i],
                personality=personality,
                initial_wealth=economic_data['wealth'][i],
                initial_location=location
            )
            
            # Set custom internal state values
            agent.internal_state.mood = state_data['mood'][i]
            agent.internal_state.stress = state_data['stress'][i]
            agent.internal_state.self_control_resource = state_data['self_control'][i]
            agent.internal_state.monthly_expenses = economic_data['expenses'][i]
            
            # Set initial behavioral states
            agent.habit_stocks[BehaviorType.DRINKING] = behavioral_data['drinking_habit'][i]
            agent.habit_stocks[BehaviorType.GAMBLING] = behavioral_data['gambling_habit'][i]
            
            # Set initial addiction state
            agent.addiction_states[SubstanceType.ALCOHOL].stock = behavioral_data['addiction_stock'][i]
            
            agents.append(agent)
        
        self.generation_stats['total_generated'] += size
        return agents
    
    def _generate_personality_traits(self, size: int) -> Dict[str, np.ndarray]:
        """Generate personality trait arrays for all agents."""
        traits = {}
        
        for trait_name, dist_spec in self.config.personality_traits.items():
            traits[trait_name] = dist_spec.sample(size)
            
            # Track ranges for statistics
            self.generation_stats['attribute_ranges'][f'personality_{trait_name}'] = {
                'min': float(np.min(traits[trait_name])),
                'max': float(np.max(traits[trait_name])),
                'mean': float(np.mean(traits[trait_name])),
                'std': float(np.std(traits[trait_name]))
            }
        
        return traits
    
    def _generate_economic_attributes(self, size: int) -> Dict[str, np.ndarray]:
        """Generate economic attributes for all agents."""
        wealth = self.config.initial_wealth.sample(size)
        expenses = self.config.monthly_expenses.sample(size)
        
        # Track statistics
        self.generation_stats['attribute_ranges']['wealth'] = {
            'min': float(np.min(wealth)),
            'max': float(np.max(wealth)),
            'mean': float(np.mean(wealth)),
            'std': float(np.std(wealth))
        }
        
        self.generation_stats['attribute_ranges']['expenses'] = {
            'min': float(np.min(expenses)),
            'max': float(np.max(expenses)),
            'mean': float(np.mean(expenses)),
            'std': float(np.std(expenses))
        }
        
        return {
            'wealth': wealth,
            'expenses': expenses
        }
    
    def _generate_initial_states(self, size: int) -> Dict[str, np.ndarray]:
        """Generate initial internal state values."""
        mood = self.config.initial_mood.sample(size)
        stress = self.config.initial_stress.sample(size)
        self_control = self.config.initial_self_control.sample(size)
        
        # Track statistics
        for name, values in [('mood', mood), ('stress', stress), ('self_control', self_control)]:
            self.generation_stats['attribute_ranges'][f'initial_{name}'] = {
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'mean': float(np.mean(values)),
                'std': float(np.std(values))
            }
        
        return {
            'mood': mood,
            'stress': stress,
            'self_control': self_control
        }
    
    def _generate_behavioral_states(self, size: int) -> Dict[str, np.ndarray]:
        """Generate initial behavioral states."""
        drinking_habit = self.config.initial_drinking_habit.sample(size)
        gambling_habit = self.config.initial_gambling_habit.sample(size)
        addiction_stock = self.config.initial_addiction_stock.sample(size)
        
        # Track statistics
        for name, values in [('drinking_habit', drinking_habit), 
                           ('gambling_habit', gambling_habit),
                           ('addiction_stock', addiction_stock)]:
            self.generation_stats['attribute_ranges'][f'behavioral_{name}'] = {
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'mean': float(np.mean(values)),
                'std': float(np.std(values))
            }
        
        return {
            'drinking_habit': drinking_habit,
            'gambling_habit': gambling_habit,
            'addiction_stock': addiction_stock
        }
    
    def _generate_demographic_attributes(self, size: int, name_prefix: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate demographic attributes like names."""
        # Generate names
        if name_prefix:
            names = [f"{name_prefix}_{i:04d}" for i in range(size)]
        else:
            # Sample from name categories
            base_names = self.config.name_categories.sample(size)
            names = [f"{name}_{i:04d}" for i, name in enumerate(base_names)]
        
        return {
            'names': names
        }
    
    def generate_test_population(self, size: int = 10) -> List[Agent]:
        """Generate a small test population for validation."""
        return self.generate_population(size)
    
    def generate_stratified_population(
        self, 
        total_size: int,
        strata_proportions: Dict[str, float],
        strata_configs: Dict[str, DistributionConfig]
    ) -> List[Agent]:
        """
        Generate a stratified population with different distribution configs for different groups.
        
        Args:
            total_size: Total population size
            strata_proportions: Dict mapping stratum name to proportion (should sum to 1.0)
            strata_configs: Dict mapping stratum name to DistributionConfig
            
        Returns:
            Combined list of agents from all strata
        """
        agents = []
        
        for stratum_name, proportion in strata_proportions.items():
            stratum_size = int(total_size * proportion)
            stratum_config = strata_configs[stratum_name]
            
            # Create temporary generator for this stratum
            stratum_generator = PopulationGenerator(stratum_config, self.seed)
            stratum_agents = stratum_generator.generate_population(
                stratum_size, 
                name_prefix=stratum_name
            )
            
            agents.extend(stratum_agents)
            
            # Update our statistics
            for key, value in stratum_generator.generation_stats.items():
                if key == 'total_generated':
                    self.generation_stats[key] += value
                elif key == 'attribute_ranges':
                    # Merge attribute ranges (simplified)
                    self.generation_stats[key].update(value)
        
        return agents
    
    def create_agent_profiles_sample(self, size: int = 50) -> List[Dict[str, Any]]:
        """
        Create a sample of agent profiles without full Agent objects for quick review.
        
        Args:
            size: Number of profiles to generate
            
        Returns:
            List of dictionaries with agent attribute summaries
        """
        profiles = []
        
        # Generate attributes
        personality_data = self._generate_personality_traits(size)
        economic_data = self._generate_economic_attributes(size)
        state_data = self._generate_initial_states(size)
        behavioral_data = self._generate_behavioral_states(size)
        demographic_data = self._generate_demographic_attributes(size)
        
        for i in range(size):
            profile = {
                'name': demographic_data['names'][i],
                'personality': {
                    trait: float(values[i]) 
                    for trait, values in personality_data.items()
                },
                'economic': {
                    'wealth': float(economic_data['wealth'][i]),
                    'monthly_expenses': float(economic_data['expenses'][i])
                },
                'initial_state': {
                    'mood': float(state_data['mood'][i]),
                    'stress': float(state_data['stress'][i]),
                    'self_control': float(state_data['self_control'][i])
                },
                'behavioral': {
                    'drinking_habit': float(behavioral_data['drinking_habit'][i]),
                    'gambling_habit': float(behavioral_data['gambling_habit'][i]),
                    'addiction_stock': float(behavioral_data['addiction_stock'][i])
                }
            }
            profiles.append(profile)
        
        return profiles
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of generation statistics."""
        return {
            'config_summary': self.config.get_summary(),
            'generation_stats': self.generation_stats,
            'seed': self.seed
        }
    
    def update_config(self, new_config: DistributionConfig) -> None:
        """Update the distribution configuration."""
        self.config = new_config
        
    def clone_with_seed(self, new_seed: int) -> 'PopulationGenerator':
        """Create a copy of this generator with a new seed."""
        return PopulationGenerator(self.config, new_seed)


class QuickPopulationFactory:
    """Factory class for creating common population types quickly."""
    
    @staticmethod
    def create_balanced_population(size: int, seed: Optional[int] = None) -> List[Agent]:
        """Create a balanced, realistic population."""
        config = DistributionConfig.create_realistic_default()
        generator = PopulationGenerator(config, seed)
        return generator.generate_population(size)
    
    @staticmethod
    def create_diverse_population(size: int, seed: Optional[int] = None) -> List[Agent]:
        """Create a maximally diverse population."""
        config = DistributionConfig.create_diverse_population()
        generator = PopulationGenerator(config, seed)
        return generator.generate_population(size)
    
    @staticmethod
    def create_vulnerable_population(size: int, seed: Optional[int] = None) -> List[Agent]:
        """Create a population with higher addiction vulnerability."""
        config = DistributionConfig.create_vulnerable_population()
        generator = PopulationGenerator(config, seed)
        return generator.generate_population(size)
    
    @staticmethod
    def create_mixed_population(
        size: int, 
        vulnerable_proportion: float = 0.2, 
        seed: Optional[int] = None
    ) -> List[Agent]:
        """Create a mixed population with vulnerable and balanced agents."""
        total_size = size
        strata_proportions = {
            'vulnerable': vulnerable_proportion,
            'balanced': 1.0 - vulnerable_proportion
        }
        strata_configs = {
            'vulnerable': DistributionConfig.create_vulnerable_population(),
            'balanced': DistributionConfig.create_realistic_default()
        }
        
        # Use balanced config as base for generator
        generator = PopulationGenerator(DistributionConfig.create_realistic_default(), seed)
        return generator.generate_stratified_population(total_size, strata_proportions, strata_configs) 