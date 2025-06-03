"""
Tests for the Environmental Cue System.
"""
import pytest
import math
from unittest.mock import Mock, MagicMock

from src.environment.cues import CueGenerator, CueSource
from src.utils.types import (
    CueType, PlotID, Coordinate, SimulationTime, 
    AlcoholCue, GamblingCue, FinancialStressCue,
    PersonalityTraits, InternalState, AddictionState,
    SubstanceType, BehaviorType
)


class TestCueGenerator:
    """Test the CueGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cue_generator = CueGenerator()
    
    def test_calculate_cue_intensity_at_source(self):
        """Test cue intensity calculation at the source (distance=0)."""
        base_intensity = 0.8
        intensity = self.cue_generator.calculate_cue_intensity(
            distance=0.0,
            base_intensity=base_intensity
        )
        assert intensity == base_intensity
    
    def test_calculate_cue_intensity_distance_decay(self):
        """Test that cue intensity decreases with distance."""
        base_intensity = 1.0
        max_radius = 3.0
        
        # Test multiple distances
        distances = [0.5, 1.0, 2.0, 2.5]
        intensities = []
        
        for distance in distances:
            intensity = self.cue_generator.calculate_cue_intensity(
                distance=distance,
                base_intensity=base_intensity,
                max_radius=max_radius
            )
            intensities.append(intensity)
        
        # Intensity should decrease with distance
        for i in range(1, len(intensities)):
            assert intensities[i] < intensities[i-1], f"Intensity should decrease with distance"
    
    def test_calculate_cue_intensity_beyond_radius(self):
        """Test that cue intensity is zero beyond max radius."""
        intensity = self.cue_generator.calculate_cue_intensity(
            distance=5.0,
            base_intensity=1.0,
            max_radius=3.0
        )
        assert intensity == 0.0
    
    def test_create_cue_types(self):
        """Test creation of different cue types."""
        plot_id = PlotID("test_plot")
        
        # Test alcohol cue
        alcohol_cue = self.cue_generator._create_cue(
            CueType.ALCOHOL_CUE, 0.5, plot_id
        )
        assert isinstance(alcohol_cue, AlcoholCue)
        assert alcohol_cue.intensity == 0.5
        assert alcohol_cue.source == plot_id
        assert alcohol_cue.cue_type == CueType.ALCOHOL_CUE
        
        # Test gambling cue
        gambling_cue = self.cue_generator._create_cue(
            CueType.GAMBLING_CUE, 0.7, plot_id
        )
        assert isinstance(gambling_cue, GamblingCue)
        assert gambling_cue.intensity == 0.7
        
        # Test financial stress cue
        stress_cue = self.cue_generator._create_cue(
            CueType.FINANCIAL_STRESS_CUE, 0.3, plot_id
        )
        assert isinstance(stress_cue, FinancialStressCue)
        assert stress_cue.intensity == 0.3
    
    def test_agent_state_modulation_alcohol_addiction(self):
        """Test that alcohol addiction amplifies alcohol cues."""
        # Create mock agent with alcohol addiction
        agent = Mock()
        agent.addiction_states = {
            SubstanceType.ALCOHOL: AddictionState(
                stock=0.6,
                withdrawal_severity=0.4
            )
        }
        agent.internal_state = InternalState(stress=0.3)
        
        base_intensity = 0.5
        modulated_intensity = self.cue_generator._apply_agent_state_modulation(
            base_intensity, CueType.ALCOHOL_CUE, agent
        )
        
        # Should be amplified due to addiction
        assert modulated_intensity > base_intensity
    
    def test_agent_state_modulation_gambling_financial_pressure(self):
        """Test that financial pressure amplifies gambling cues."""
        agent = Mock()
        agent.habit_stocks = {BehaviorType.GAMBLING: 0.3}
        agent.internal_state = InternalState(
            wealth=500.0,
            monthly_expenses=800.0  # Can't afford expenses
        )
        
        base_intensity = 0.4
        modulated_intensity = self.cue_generator._apply_agent_state_modulation(
            base_intensity, CueType.GAMBLING_CUE, agent
        )
        
        # Should be amplified due to financial pressure
        assert modulated_intensity > base_intensity
    
    def test_agent_state_modulation_stress_alcohol(self):
        """Test that high stress amplifies alcohol cues."""
        agent = Mock()
        agent.addiction_states = {SubstanceType.ALCOHOL: AddictionState()}
        agent.internal_state = InternalState(stress=0.8)  # High stress
        
        base_intensity = 0.3
        modulated_intensity = self.cue_generator._apply_agent_state_modulation(
            base_intensity, CueType.ALCOHOL_CUE, agent
        )
        
        # Should be amplified due to high stress
        assert modulated_intensity > base_intensity
    
    def test_temporal_cues_financial_stress(self):
        """Test generation of financial stress temporal cues."""
        # Create agent with financial pressure
        agent = Mock()
        agent.internal_state = InternalState(
            wealth=400.0,
            monthly_expenses=800.0
        )
        
        # Time near end of month
        time = SimulationTime(month=6, year=1)
        time.month_progress = 0.9
        
        cues = self.cue_generator.generate_temporal_cues(agent, time)
        
        # Should generate financial stress cue
        stress_cues = [c for c in cues if c.cue_type == CueType.FINANCIAL_STRESS_CUE]
        assert len(stress_cues) > 0
        assert stress_cues[0].intensity > 0
    
    def test_temporal_cues_withdrawal(self):
        """Test generation of withdrawal cues."""
        agent = Mock()
        agent.addiction_states = {
            SubstanceType.ALCOHOL: AddictionState(
                stock=0.4,
                withdrawal_severity=0.6
            )
        }
        agent.habit_stocks = {BehaviorType.DRINKING: 0.1}
        
        time = SimulationTime()
        cues = self.cue_generator.generate_temporal_cues(agent, time)
        
        # Should generate withdrawal cue
        withdrawal_cues = [c for c in cues if c.cue_type == CueType.ALCOHOL_CUE and c.source is None]
        assert len(withdrawal_cues) > 0
    
    def test_social_cues_modeling(self):
        """Test generation of social modeling cues."""
        # Observer agent
        observer = Mock()
        
        # Observed agent with strong drinking habit
        observed = Mock()
        observed.id = "other_agent"
        observed.habit_stocks = {
            BehaviorType.DRINKING: 0.8,
            BehaviorType.GAMBLING: 0.3
        }
        
        cues = self.cue_generator.generate_social_cues(observer, [observed])
        
        # Should generate social modeling cue for drinking
        alcohol_cues = [c for c in cues if c.cue_type == CueType.ALCOHOL_CUE]
        assert len(alcohol_cues) > 0
        assert alcohol_cues[0].intensity > 0
    
    def test_spatial_cues_integration(self):
        """Test spatial cue generation integration."""
        # Create mock city with districts and buildings
        city = Mock()
        
        # Mock district with plots
        district = Mock()
        
        # Create plot with liquor store
        plot = Mock()
        plot.id = PlotID("liquor_plot")
        plot.location = (2.0, 1.0)
        plot.building = Mock()
        plot.building.plot = plot
        type(plot.building).__name__ = 'LiquorStore'
        
        district.plots = [plot]
        city.districts = [district]
        
        # Mock agent
        agent = Mock()
        agent.current_location = PlotID("agent_plot")
        agent.addiction_states = {SubstanceType.ALCOHOL: AddictionState()}
        agent.internal_state = InternalState()
        
        # Mock agent plot
        agent_plot = Mock()
        agent_plot.location = (0.0, 0.0)
        city.get_plot.return_value = agent_plot
        
        cues = self.cue_generator.generate_spatial_cues(agent, city)
        
        # Should generate alcohol cue from liquor store
        alcohol_cues = [c for c in cues if c.cue_type == CueType.ALCOHOL_CUE]
        assert len(alcohol_cues) > 0
        assert alcohol_cues[0].source == plot.id
    
    def test_cue_intensity_mathematical_properties(self):
        """Test mathematical properties of cue intensity function."""
        base_intensity = 0.8
        max_radius = 3.0
        
        # Test that intensity at distance 0 equals base intensity
        assert self.cue_generator.calculate_cue_intensity(0, base_intensity, max_radius) == base_intensity
        
        # Test that intensity is always non-negative
        for distance in [0.1, 0.5, 1.0, 2.0, 2.9]:
            intensity = self.cue_generator.calculate_cue_intensity(distance, base_intensity, max_radius)
            assert intensity >= 0
        
        # Test that intensity never exceeds base intensity
        for distance in [0.1, 0.5, 1.0, 2.0]:
            intensity = self.cue_generator.calculate_cue_intensity(distance, base_intensity, max_radius)
            assert intensity <= base_intensity
        
        # Test continuity - small changes in distance should produce small changes in intensity
        intensity_1 = self.cue_generator.calculate_cue_intensity(1.0, base_intensity, max_radius)
        intensity_2 = self.cue_generator.calculate_cue_intensity(1.1, base_intensity, max_radius)
        assert abs(intensity_1 - intensity_2) < 0.2  # Should be continuous


class TestCueIntegration:
    """Integration tests for the complete cue system."""
    
    def test_combined_cue_effects(self):
        """Test how multiple cues combine to influence agent state."""
        agent = Mock()
        agent.addiction_states = {
            SubstanceType.ALCOHOL: AddictionState(stock=0.5, withdrawal_severity=0.3)
        }
        agent.habit_stocks = {
            BehaviorType.GAMBLING: 0.4,
            BehaviorType.DRINKING: 0.6
        }
        agent.internal_state = InternalState(
            wealth=600.0,
            monthly_expenses=800.0,
            stress=0.7
        )
        
        cue_generator = CueGenerator()
        
        # Test various cue modulations
        alcohol_intensity = cue_generator._apply_agent_state_modulation(
            0.5, CueType.ALCOHOL_CUE, agent
        )
        gambling_intensity = cue_generator._apply_agent_state_modulation(
            0.4, CueType.GAMBLING_CUE, agent
        )
        
        # Both should be amplified due to agent state
        assert alcohol_intensity > 0.5
        assert gambling_intensity > 0.4
    
    def test_realistic_cue_scenario(self):
        """Test a realistic scenario with multiple cue sources."""
        cue_generator = CueGenerator()
        
        # Vulnerable agent near multiple cue sources
        agent = Mock()
        agent.current_location = PlotID("agent_location")
        agent.addiction_states = {
            SubstanceType.ALCOHOL: AddictionState(
                stock=0.7,
                withdrawal_severity=0.5,
                time_since_last_use=2
            )
        }
        agent.habit_stocks = {
            BehaviorType.DRINKING: 0.8,
            BehaviorType.GAMBLING: 0.3
        }
        agent.internal_state = InternalState(
            wealth=300.0,
            monthly_expenses=800.0,
            stress=0.8
        )
        
        # Multiple nearby cue sources
        time = SimulationTime()
        time.month_progress = 0.85  # Near end of month
        
        # Should generate strong temporal cues due to agent's vulnerable state
        temporal_cues = cue_generator.generate_temporal_cues(agent, time)
        
        # Should have withdrawal cues and financial stress cues
        withdrawal_cues = [c for c in temporal_cues if c.cue_type == CueType.ALCOHOL_CUE]
        stress_cues = [c for c in temporal_cues if c.cue_type == CueType.FINANCIAL_STRESS_CUE]
        
        assert len(withdrawal_cues) > 0
        assert len(stress_cues) > 0
        
        # Cues should be intense due to agent's vulnerable state
        assert any(c.intensity > 0.5 for c in temporal_cues)


if __name__ == "__main__":
    pytest.main([__file__]) 