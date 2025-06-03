"""
Population analysis tools for reviewing generated populations.

Provides statistical analysis, visualization-ready data, and validation
tools for agent populations before running simulations.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from src.agents.agent import Agent
from src.utils.types import BehaviorType, SubstanceType


@dataclass
class PopulationStats:
    """Statistical summary of a population."""
    size: int
    
    # Personality trait statistics
    personality_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Economic statistics
    wealth_stats: Dict[str, float] = field(default_factory=dict)
    expense_stats: Dict[str, float] = field(default_factory=dict)
    
    # Initial state statistics
    mood_stats: Dict[str, float] = field(default_factory=dict)
    stress_stats: Dict[str, float] = field(default_factory=dict)
    self_control_stats: Dict[str, float] = field(default_factory=dict)
    
    # Behavioral statistics
    drinking_habit_stats: Dict[str, float] = field(default_factory=dict)
    gambling_habit_stats: Dict[str, float] = field(default_factory=dict)
    addiction_stock_stats: Dict[str, float] = field(default_factory=dict)
    
    # Distribution validation
    distribution_warnings: List[str] = field(default_factory=list)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for easy printing/export."""
        return {
            'Population Size': self.size,
            'Personality Traits': self.personality_stats,
            'Economic': {
                'Wealth': self.wealth_stats,
                'Monthly Expenses': self.expense_stats
            },
            'Initial States': {
                'Mood': self.mood_stats,
                'Stress': self.stress_stats,
                'Self Control': self.self_control_stats
            },
            'Behavioral': {
                'Drinking Habits': self.drinking_habit_stats,
                'Gambling Habits': self.gambling_habit_stats,
                'Addiction Stock': self.addiction_stock_stats
            },
            'Warnings': self.distribution_warnings
        }


class PopulationAnalyzer:
    """Analyzes agent populations and provides review tools."""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_population(self, agents: List[Agent]) -> PopulationStats:
        """
        Perform comprehensive analysis of an agent population.
        
        Args:
            agents: List of agents to analyze
            
        Returns:
            PopulationStats object with comprehensive statistics
        """
        if not agents:
            return PopulationStats(size=0)
        
        stats = PopulationStats(size=len(agents))
        
        # Extract all attributes into arrays for analysis
        personality_data = self._extract_personality_data(agents)
        economic_data = self._extract_economic_data(agents)
        state_data = self._extract_state_data(agents)
        behavioral_data = self._extract_behavioral_data(agents)
        
        # Compute statistics
        stats.personality_stats = self._compute_stats_dict(personality_data)
        stats.wealth_stats = self._compute_stats(economic_data['wealth'])
        stats.expense_stats = self._compute_stats(economic_data['expenses'])
        stats.mood_stats = self._compute_stats(state_data['mood'])
        stats.stress_stats = self._compute_stats(state_data['stress'])
        stats.self_control_stats = self._compute_stats(state_data['self_control'])
        stats.drinking_habit_stats = self._compute_stats(behavioral_data['drinking_habit'])
        stats.gambling_habit_stats = self._compute_stats(behavioral_data['gambling_habit'])
        stats.addiction_stock_stats = self._compute_stats(behavioral_data['addiction_stock'])
        
        # Validate distributions and add warnings
        stats.distribution_warnings = self._validate_distributions(agents, stats)
        
        return stats
    
    def _extract_personality_data(self, agents: List[Agent]) -> Dict[str, np.ndarray]:
        """Extract personality trait data from agents."""
        traits = {
            'baseline_impulsivity': [],
            'risk_preference_alpha': [],
            'risk_preference_beta': [],
            'risk_preference_lambda': [],
            'cognitive_type': [],
            'addiction_vulnerability': [],
            'gambling_bias_strength': []
        }
        
        for agent in agents:
            traits['baseline_impulsivity'].append(agent.personality.baseline_impulsivity)
            traits['risk_preference_alpha'].append(agent.personality.risk_preference_alpha)
            traits['risk_preference_beta'].append(agent.personality.risk_preference_beta)
            traits['risk_preference_lambda'].append(agent.personality.risk_preference_lambda)
            traits['cognitive_type'].append(agent.personality.cognitive_type)
            traits['addiction_vulnerability'].append(agent.personality.addiction_vulnerability)
            traits['gambling_bias_strength'].append(agent.personality.gambling_bias_strength)
        
        return {k: np.array(v) for k, v in traits.items()}
    
    def _extract_economic_data(self, agents: List[Agent]) -> Dict[str, np.ndarray]:
        """Extract economic data from agents."""
        wealth = [agent.internal_state.wealth for agent in agents]
        expenses = [agent.internal_state.monthly_expenses for agent in agents]
        
        return {
            'wealth': np.array(wealth),
            'expenses': np.array(expenses)
        }
    
    def _extract_state_data(self, agents: List[Agent]) -> Dict[str, np.ndarray]:
        """Extract initial state data from agents."""
        mood = [agent.internal_state.mood for agent in agents]
        stress = [agent.internal_state.stress for agent in agents]
        self_control = [agent.internal_state.self_control_resource for agent in agents]
        
        return {
            'mood': np.array(mood),
            'stress': np.array(stress),
            'self_control': np.array(self_control)
        }
    
    def _extract_behavioral_data(self, agents: List[Agent]) -> Dict[str, np.ndarray]:
        """Extract behavioral state data from agents."""
        drinking_habit = [agent.habit_stocks[BehaviorType.DRINKING] for agent in agents]
        gambling_habit = [agent.habit_stocks[BehaviorType.GAMBLING] for agent in agents]
        addiction_stock = [agent.addiction_states[SubstanceType.ALCOHOL].stock for agent in agents]
        
        return {
            'drinking_habit': np.array(drinking_habit),
            'gambling_habit': np.array(gambling_habit),
            'addiction_stock': np.array(addiction_stock)
        }
    
    def _compute_stats(self, values: np.ndarray) -> Dict[str, float]:
        """Compute statistical summary for a single attribute."""
        if len(values) == 0:
            return {}
            
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'q25': float(np.percentile(values, 25)),
            'q75': float(np.percentile(values, 75))
        }
    
    def _compute_stats_dict(self, data_dict: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Compute statistics for a dictionary of arrays."""
        return {key: self._compute_stats(values) for key, values in data_dict.items()}
    
    def _validate_distributions(self, agents: List[Agent], stats: PopulationStats) -> List[str]:
        """Validate population distributions and return warnings."""
        warnings = []
        
        # Check for extremely skewed distributions
        for trait_name, trait_stats in stats.personality_stats.items():
            if trait_stats['std'] < 0.05:
                warnings.append(f"Very low variance in {trait_name} (std={trait_stats['std']:.3f})")
        
        # Check for unrealistic wealth distributions
        wealth_ratio = stats.wealth_stats['max'] / max(stats.wealth_stats['min'], 1.0)
        if wealth_ratio > 1000:
            warnings.append(f"Extreme wealth inequality (max/min ratio: {wealth_ratio:.1f})")
        
        # Check for agents who can't afford expenses
        broke_agents = sum(1 for agent in agents 
                          if agent.internal_state.wealth < agent.internal_state.monthly_expenses)
        if broke_agents > len(agents) * 0.5:
            warnings.append(f"{broke_agents}/{len(agents)} agents can't afford monthly expenses")
        
        # Check for high initial addiction rates
        high_addiction = sum(1 for agent in agents 
                           if agent.addiction_states[SubstanceType.ALCOHOL].stock > 0.3)
        if high_addiction > len(agents) * 0.1:
            warnings.append(f"{high_addiction}/{len(agents)} agents start with high addiction levels")
        
        return warnings
    
    def create_dataframe(self, agents: List[Agent]) -> pd.DataFrame:
        """
        Create a pandas DataFrame with all agent attributes for analysis.
        
        Args:
            agents: List of agents to convert
            
        Returns:
            DataFrame with agent attributes
        """
        data = []
        
        for agent in agents:
            row = {
                'agent_id': agent.id,
                'name': agent.name,
                
                # Personality traits
                'baseline_impulsivity': agent.personality.baseline_impulsivity,
                'risk_preference_alpha': agent.personality.risk_preference_alpha,
                'risk_preference_beta': agent.personality.risk_preference_beta,
                'risk_preference_lambda': agent.personality.risk_preference_lambda,
                'cognitive_type': agent.personality.cognitive_type,
                'addiction_vulnerability': agent.personality.addiction_vulnerability,
                'gambling_bias_strength': agent.personality.gambling_bias_strength,
                
                # Economic state
                'wealth': agent.internal_state.wealth,
                'monthly_expenses': agent.internal_state.monthly_expenses,
                'expense_ratio': agent.internal_state.monthly_expenses / max(agent.internal_state.wealth, 1),
                
                # Internal state
                'mood': agent.internal_state.mood,
                'stress': agent.internal_state.stress,
                'self_control_resource': agent.internal_state.self_control_resource,
                
                # Behavioral states
                'drinking_habit': agent.habit_stocks[BehaviorType.DRINKING],
                'gambling_habit': agent.habit_stocks[BehaviorType.GAMBLING],
                'addiction_stock': agent.addiction_states[SubstanceType.ALCOHOL].stock,
                
                # Derived metrics
                'financial_stress': 1.0 if agent.internal_state.wealth < agent.internal_state.monthly_expenses else 0.0,
                'high_risk_profile': 1.0 if (agent.personality.baseline_impulsivity > 0.7 and 
                                           agent.personality.addiction_vulnerability > 0.6) else 0.0
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_distribution_overview(self, agents: List[Agent]) -> Dict[str, Any]:
        """
        Get a high-level overview of population distributions.
        
        Args:
            agents: List of agents to analyze
            
        Returns:
            Dictionary with distribution summaries
        """
        if not agents:
            return {}
        
        df = self.create_dataframe(agents)
        
        overview = {
            'size': len(agents),
            'summary': {
                'financial_stress_rate': df['financial_stress'].mean(),
                'high_risk_rate': df['high_risk_profile'].mean(),
                'mean_wealth': df['wealth'].mean(),
                'wealth_inequality_gini': self._calculate_gini(df['wealth']),
                'addiction_vulnerability_mean': df['addiction_vulnerability'].mean(),
                'impulsivity_mean': df['baseline_impulsivity'].mean()
            },
            'correlations': {
                'wealth_stress': df['wealth'].corr(df['stress']),
                'impulsivity_addiction_vuln': df['baseline_impulsivity'].corr(df['addiction_vulnerability']),
                'stress_self_control': df['stress'].corr(df['self_control_resource'])
            },
            'extremes': {
                'wealthiest_agent': df.loc[df['wealth'].idxmax()]['name'],
                'most_stressed_agent': df.loc[df['stress'].idxmax()]['name'],
                'most_impulsive_agent': df.loc[df['baseline_impulsivity'].idxmax()]['name']
            }
        }
        
        return overview
    
    def _calculate_gini(self, values: pd.Series) -> float:
        """Calculate Gini coefficient for inequality measurement."""
        values = values.sort_values()
        n = len(values)
        cumsum = values.cumsum()
        return (n + 1 - 2 * cumsum.sum() / values.sum()) / n
    
    def compare_populations(self, pop1: List[Agent], pop2: List[Agent], 
                          labels: Tuple[str, str] = ("Population 1", "Population 2")) -> Dict[str, Any]:
        """
        Compare two populations statistically.
        
        Args:
            pop1: First population
            pop2: Second population 
            labels: Labels for the populations
            
        Returns:
            Comparison results
        """
        stats1 = self.analyze_population(pop1)
        stats2 = self.analyze_population(pop2)
        
        comparison = {
            'sizes': {labels[0]: stats1.size, labels[1]: stats2.size},
            'personality_differences': {},
            'economic_differences': {},
            'state_differences': {}
        }
        
        # Compare personality traits
        for trait in stats1.personality_stats:
            if trait in stats2.personality_stats:
                mean_diff = (stats2.personality_stats[trait]['mean'] - 
                           stats1.personality_stats[trait]['mean'])
                comparison['personality_differences'][trait] = {
                    'mean_difference': mean_diff,
                    'pop1_mean': stats1.personality_stats[trait]['mean'],
                    'pop2_mean': stats2.personality_stats[trait]['mean']
                }
        
        # Compare economic attributes
        wealth_diff = stats2.wealth_stats['mean'] - stats1.wealth_stats['mean']
        comparison['economic_differences']['wealth'] = {
            'mean_difference': wealth_diff,
            'pop1_mean': stats1.wealth_stats['mean'],
            'pop2_mean': stats2.wealth_stats['mean']
        }
        
        # Compare stress levels
        stress_diff = stats2.stress_stats['mean'] - stats1.stress_stats['mean']
        comparison['state_differences']['stress'] = {
            'mean_difference': stress_diff,
            'pop1_mean': stats1.stress_stats['mean'],
            'pop2_mean': stats2.stress_stats['mean']
        }
        
        return comparison
    
    def get_agent_profiles_summary(self, agents: List[Agent], n_profiles: int = 10) -> List[Dict[str, Any]]:
        """
        Get detailed profiles for a sample of agents.
        
        Args:
            agents: List of agents
            n_profiles: Number of agent profiles to return
            
        Returns:
            List of detailed agent profiles
        """
        if len(agents) <= n_profiles:
            sample_agents = agents
        else:
            # Sample diverse agents
            indices = np.linspace(0, len(agents) - 1, n_profiles, dtype=int)
            sample_agents = [agents[i] for i in indices]
        
        profiles = []
        for agent in sample_agents:
            profile = {
                'id': agent.id,
                'name': agent.name,
                'personality_summary': {
                    'impulsivity': f"{agent.personality.baseline_impulsivity:.2f}",
                    'risk_aversion': f"{agent.personality.risk_preference_lambda:.2f}", 
                    'cognitive_type': f"{agent.personality.cognitive_type:.2f}",
                    'addiction_vulnerability': f"{agent.personality.addiction_vulnerability:.2f}"
                },
                'economic_situation': {
                    'wealth': f"${agent.internal_state.wealth:,.0f}",
                    'monthly_expenses': f"${agent.internal_state.monthly_expenses:,.0f}",
                    'months_of_savings': f"{agent.internal_state.wealth / agent.internal_state.monthly_expenses:.1f}"
                },
                'current_state': {
                    'mood': f"{agent.internal_state.mood:+.2f}",
                    'stress': f"{agent.internal_state.stress:.2f}",
                    'self_control': f"{agent.internal_state.self_control_resource:.2f}"
                },
                'risk_factors': {
                    'drinking_habit': f"{agent.habit_stocks[BehaviorType.DRINKING]:.3f}",
                    'gambling_habit': f"{agent.habit_stocks[BehaviorType.GAMBLING]:.3f}",
                    'addiction_stock': f"{agent.addiction_states[SubstanceType.ALCOHOL].stock:.3f}"
                }
            }
            profiles.append(profile)
        
        return profiles
    
    def export_analysis_report(self, agents: List[Agent], filepath: str) -> None:
        """
        Export a comprehensive analysis report to a file.
        
        Args:
            agents: List of agents to analyze
            filepath: Output file path
        """
        stats = self.analyze_population(agents)
        overview = self.get_distribution_overview(agents)
        profiles = self.get_agent_profiles_summary(agents, 20)
        
        report = {
            'population_statistics': stats.to_summary_dict(),
            'distribution_overview': overview,
            'sample_agent_profiles': profiles,
            'analysis_metadata': {
                'total_agents_analyzed': len(agents),
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
        }
        
        if filepath.endswith('.json'):
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
        else:
            # Export as text report
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("POPULATION ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Population Size: {stats.size}\n\n")
                
                f.write("DISTRIBUTION OVERVIEW\n")
                f.write("-" * 20 + "\n")
                for key, value in overview['summary'].items():
                    f.write(f"{key}: {value:.3f}\n")
                
                f.write("\nWARNINGS\n")
                f.write("-" * 10 + "\n")
                for warning in stats.distribution_warnings:
                    f.write(f"WARNING: {warning}\n")
                
                f.write(f"\nSample Agent Profiles ({len(profiles)} agents)\n")
                f.write("-" * 30 + "\n")
                for profile in profiles[:5]:  # Show first 5
                    f.write(f"\n{profile['name']} ({profile['id'][:8]}...)\n")
                    f.write(f"  Wealth: {profile['economic_situation']['wealth']}\n")
                    f.write(f"  Impulsivity: {profile['personality_summary']['impulsivity']}\n")
                    f.write(f"  Stress: {profile['current_state']['stress']}\n") 