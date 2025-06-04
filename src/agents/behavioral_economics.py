"""
Behavioral economics modules implementing psychological theories.
"""
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

from src.utils.types import PersonalityTraits, GamblingContext


class ProspectTheoryModule:
    """Implements Kahneman-Tversky Prospect Theory for value evaluation."""
    
    @staticmethod
    def evaluate_outcome(
        outcome: float, 
        reference_point: float, 
        personality: PersonalityTraits
    ) -> float:
        """
        Evaluate an outcome using prospect theory value function.
        
        Args:
            outcome: The actual outcome value
            reference_point: Reference point for gains/losses
            personality: Agent's personality traits including risk preferences
            
        Returns:
            Subjective value of the outcome
        """
        deviation = outcome - reference_point
        
        if deviation >= 0:
            # Gains - concave value function
            value = deviation ** personality.risk_preference_alpha
        else:
            # Losses - convex value function with loss aversion
            value = -personality.risk_preference_lambda * (
                (-deviation) ** personality.risk_preference_beta
            )
            
        return value
    
    @staticmethod
    def weight_probability(
        probability: float, 
        context: str = "DEFAULT"
    ) -> float:
        """
        Apply probability weighting function.
        
        Args:
            probability: Objective probability [0,1]
            context: Context for weighting (e.g., "GAMBLING")
            
        Returns:
            Weighted probability
        """
        if probability <= 0:
            return 0.0
        if probability >= 1:
            return 1.0
            
        if context == "GAMBLING":
            # Kahneman-Tversky weighting - overweight small probabilities
            gamma = 0.69
            return (probability ** gamma) / (
                (probability ** gamma + (1 - probability) ** gamma) ** (1 / gamma)
            )
        else:
            # Default: slight overweighting of small probabilities
            gamma = 0.85
            return (probability ** gamma) / (
                (probability ** gamma + (1 - probability) ** gamma) ** (1 / gamma)
            )


class TemporalDiscountingModule:
    """Implements hyperbolic and quasi-hyperbolic discounting."""
    
    @staticmethod
    def discount_future_utility(
        utility: float,
        delay: int,  # in months
        personality: PersonalityTraits,
        cognitive_load: float = 0.0,
        craving_intensity: float = 0.0
    ) -> float:
        """
        Apply temporal discounting to future utility.
        
        Args:
            utility: Future utility value
            delay: Delay in months
            personality: Agent's personality traits
            cognitive_load: Current cognitive load [0,1]
            craving_intensity: Current craving intensity [0,1]
            
        Returns:
            Discounted present value of future utility
        """
        if delay == 0:
            return utility
            
        # Base present bias parameter
        beta = personality.baseline_impulsivity
        
        # Adjust β based on current state
        # Higher cognitive load increases present bias
        if cognitive_load > 0.7:
            beta *= 0.8  # More present-biased when cognitively loaded
            
        # High craving makes agent more myopic
        if craving_intensity > 0.5:
            beta *= (1 - craving_intensity * 0.3)
            
        # Ensure beta stays in valid range
        beta = max(0.1, min(1.0, beta))
        
        # Standard exponential discount factor
        delta = 0.95  # Monthly discount rate
        
        # Quasi-hyperbolic discounting: β * δ^t
        if delay == 1:
            return beta * utility
        else:
            return beta * (delta ** delay) * utility
    
    @staticmethod
    def calculate_hyperbolic_discount(
        utility: float,
        delay: int,
        k: float = 0.1  # Discount parameter
    ) -> float:
        """
        Pure hyperbolic discounting: V = A / (1 + k*D)
        
        Args:
            utility: Future utility
            delay: Delay in time units
            k: Discount parameter (higher = steeper discounting)
            
        Returns:
            Discounted value
        """
        return utility / (1 + k * delay)


class DualProcessModule:
    """Implements dual-process decision making (System 1 vs System 2)."""
    
    @staticmethod
    def calculate_effective_theta(
        personality: PersonalityTraits,
        self_control_resource: float,
        cognitive_load: float,
        max_craving: float,
        stress: float
    ) -> float:
        """
        Calculate effective System 2 (deliberative) weight.
        
        Args:
            personality: Agent's personality traits
            self_control_resource: Available self-control [0,1]
            cognitive_load: Current cognitive load [0,1]
            max_craving: Maximum craving intensity [0,1]
            stress: Current stress level [0,1]
            
        Returns:
            Effective theta (System 2 weight) [0,1]
        """
        # Base cognitive type
        theta_base = personality.cognitive_type
        
        # Self-control depletion reduces System 2
        theta = theta_base * self_control_resource
        
        # Cognitive load reduces deliberation
        theta *= (1 - cognitive_load * 0.5)
        
        # High craving overrides deliberation
        if max_craving > 0.7:
            craving_impact = 0.6
            theta *= (1 - max_craving * craving_impact)
            
        # High stress impairs System 2
        if stress > 0.6:
            stress_impact = 0.3
            theta *= (1 - stress * stress_impact)
            
        # Ensure minimum System 2 influence
        return max(0.1, min(1.0, theta))
    
    @staticmethod
    def combine_system_evaluations(
        system1_utility: float,
        system2_utility: float,
        theta: float
    ) -> float:
        """
        Combine System 1 and System 2 evaluations.
        
        Args:
            system1_utility: Fast, intuitive evaluation
            system2_utility: Slow, deliberative evaluation
            theta: System 2 weight [0,1]
            
        Returns:
            Combined utility
        """
        return (1 - theta) * system1_utility + theta * system2_utility


class GamblingBiasModule:
    """Implements cognitive biases specific to gambling behavior."""
    
    @staticmethod
    def apply_gamblers_fallacy(
        objective_probability: float,
        loss_streak: int,
        bias_strength: float
    ) -> float:
        """
        Apply gambler's fallacy bias to probability perception.
        
        Args:
            objective_probability: True probability of winning
            loss_streak: Number of consecutive losses
            bias_strength: Strength of gambling bias [0,1]
            
        Returns:
            Biased probability perception
        """
        if loss_streak <= 2:
            return objective_probability
            
        # Increase perceived probability with loss streak
        bias_factor = bias_strength * 0.1 * (loss_streak - 2)
        biased_prob = objective_probability + bias_factor
        
        # Cap at reasonable maximum
        return min(0.95, biased_prob)
    
    @staticmethod
    def apply_near_miss_effect(
        base_utility: float,
        was_near_miss: bool,
        bias_strength: float
    ) -> float:
        """
        Apply near-miss effect to gambling utility.
        
        Args:
            base_utility: Base utility of gambling
            was_near_miss: Whether last outcome was near-miss
            bias_strength: Strength of gambling bias [0,1]
            
        Returns:
            Modified utility
        """
        if not was_near_miss:
            return base_utility
            
        # Near-misses increase gambling appeal
        near_miss_bonus = 0.3 * bias_strength
        return base_utility + near_miss_bonus
    
    @staticmethod
    def apply_hot_hand_fallacy(
        base_utility: float,
        recent_wins: int,
        bias_strength: float
    ) -> float:
        """
        Apply hot hand fallacy - belief that wins come in streaks.
        
        Args:
            base_utility: Base utility
            recent_wins: Number of recent wins
            bias_strength: Bias strength [0,1]
            
        Returns:
            Modified utility
        """
        if recent_wins <= 1:
            return base_utility
            
        # Increase appeal with recent wins
        hot_hand_bonus = bias_strength * 0.15 * recent_wins
        return base_utility + hot_hand_bonus


class HabitFormationModule:
    """Implements habit formation and reinforcement mechanics."""
    
    @staticmethod
    def update_habit_stock(
        current_stock: float,
        consumption: float,
        lambda_param: float = 0.8
    ) -> float:
        """
        Update habit stock using exponential smoothing.
        
        Args:
            current_stock: Current habit stock level
            consumption: Current period consumption
            lambda_param: Persistence parameter [0,1]
            
        Returns:
            Updated habit stock
        """
        return lambda_param * current_stock + (1 - lambda_param) * consumption
    
    @staticmethod
    def calculate_habit_utility(
        consumption: float,
        habit_stock: float,
        phi: float = 0.5,
        base_utility_func=np.log
    ) -> float:
        """
        Calculate utility from habitual consumption.
        
        Args:
            consumption: Current consumption level
            habit_stock: Current habit stock
            phi: Habit sensitivity parameter
            base_utility_func: Base utility function
            
        Returns:
            Habit-adjusted utility
        """
        if habit_stock <= 0:
            # No habit formed yet
            return base_utility_func(max(0.01, consumption))
            
        # Multiplicative habit model
        effective_consumption = consumption / (habit_stock ** phi)
        
        # Ensure positive argument for log
        effective_consumption = max(0.01, effective_consumption)
        
        return base_utility_func(effective_consumption)


class AddictionModule:
    """Implements addiction mechanics including tolerance and withdrawal."""
    
    @staticmethod
    def calculate_withdrawal_severity(
        addiction_stock: float,
        time_since_use: int,
        max_withdrawal_time: int = 7
    ) -> float:
        """
        Calculate withdrawal severity based on addiction level and abstinence time.
        
        Args:
            addiction_stock: Current addiction capital [0,1]
            time_since_use: Days since last use
            max_withdrawal_time: Days to peak withdrawal
            
        Returns:
            Withdrawal severity [0,1]
        """
        if time_since_use == 0 or addiction_stock == 0:
            return 0.0
            
        # Base severity proportional to addiction stock
        base_severity = addiction_stock * 0.5
        
        # Time factor - peaks at max_withdrawal_time then declines
        if time_since_use <= max_withdrawal_time:
            time_factor = time_since_use / max_withdrawal_time
        else:
            # Gradual decline after peak
            time_factor = max(0, 1 - (time_since_use - max_withdrawal_time) / 14)
            
        return min(1.0, base_severity * time_factor)
    
    @staticmethod
    def calculate_tolerance_effect(
        base_effect: float,
        tolerance_level: float
    ) -> float:
        """
        Apply tolerance to reduce substance effects.
        
        Args:
            base_effect: Base effect of substance
            tolerance_level: Current tolerance [0,1]
            
        Returns:
            Tolerance-adjusted effect
        """
        # Tolerance reduces effects exponentially
        return base_effect * (1 - tolerance_level * 0.8)
    
    @staticmethod
    def update_addiction_stock(
        current_stock: float,
        consumption: float,
        decay_rate: float = 0.93,
        max_stock: float = 1.0
    ) -> float:
        """
        Update addiction stock based on consumption.
        
        Args:
            current_stock: Current addiction level
            consumption: Current consumption
            decay_rate: Monthly decay rate
            max_stock: Maximum addiction level
            
        Returns:
            Updated addiction stock
        """
        # Natural decay
        decayed_stock = current_stock * decay_rate
        
        # Increase from consumption (diminishing returns)
        increase = consumption * 0.1 * (1 - current_stock)
        
        new_stock = decayed_stock + increase
        
        return min(max_stock, new_stock) 
