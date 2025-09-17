"""
Tests for Phase 5.1 Time Management System

Tests all components:
- TimeManager class
- Monthly cycles
- Action rounds
- Event scheduling and handling
- Statistics tracking
- Time progression mechanics
"""
import unittest
from unittest.mock import Mock, MagicMock
from typing import List

from simulacra.simulation.time_manager import TimeManager, TimeEvent, ScheduledEvent, MonthlyStats
from simulacra.simulation import Simulation, SimulationConfig
from simulacra.agents.agent import Agent
from simulacra.environment.city import City
from simulacra.environment.district import District
from simulacra.environment.plot import Plot
from simulacra.utils.types import (
    PlotID, DistrictID, DistrictWealth, Coordinate, EmploymentInfo, 
    HousingInfo, EmployerID, JobID, UnitID, AgentID
)


class TestTimeManager(unittest.TestCase):
    """Test the TimeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.time_manager = TimeManager()
        
    def test_initialization(self):
        """Test TimeManager initialization."""
        self.assertEqual(self.time_manager.current_time.month, 1)
        self.assertEqual(self.time_manager.current_time.year, 1)
        self.assertEqual(self.time_manager.current_round, 0)
        self.assertEqual(self.time_manager.max_rounds_per_month, 10)
        self.assertEqual(self.time_manager.action_round_hours, 28.0)
        
    def test_agent_registration(self):
        """Test agent registration and unregistration."""
        agent_id = AgentID("test_agent")
        
        # Register agent
        self.time_manager.register_agent(agent_id)
        self.assertIn(agent_id, self.time_manager.active_agents)
        
        # Unregister agent
        self.time_manager.unregister_agent(agent_id)
        self.assertNotIn(agent_id, self.time_manager.active_agents)
        
    def test_event_scheduling(self):
        """Test event scheduling system."""
        event = ScheduledEvent(
            event_type=TimeEvent.RENT_DUE,
            data={'target_round': 5}
        )
        
        self.time_manager.schedule_event(event)
        self.assertIn(event, self.time_manager.scheduled_events)
        
    def test_event_handlers(self):
        """Test event handler registration and triggering."""
        handler_called = False
        
        def test_handler(event_type, agents, time_manager):
            nonlocal handler_called
            handler_called = True
            
        self.time_manager.add_event_handler(TimeEvent.MONTH_START, test_handler)
        self.time_manager._trigger_event(TimeEvent.MONTH_START, [], self.time_manager)
        
        self.assertTrue(handler_called)
        
    def test_rounds_configuration(self):
        """Test setting rounds per month."""
        self.time_manager.set_rounds_per_month(8)
        self.assertEqual(self.time_manager.max_rounds_per_month, 8)
        self.assertEqual(self.time_manager.action_round_hours, 35.0)  # 280/8
        
        # Test invalid input
        with self.assertRaises(ValueError):
            self.time_manager.set_rounds_per_month(0)
            
    def test_month_completion_check(self):
        """Test month completion detection."""
        self.assertFalse(self.time_manager.is_month_complete())
        
        self.time_manager.current_round = 10
        self.assertTrue(self.time_manager.is_month_complete())
        
    def test_time_info(self):
        """Test time information retrieval."""
        info = self.time_manager.get_current_time_info()
        
        self.assertEqual(info['month'], 1)
        self.assertEqual(info['year'], 1)
        self.assertEqual(info['current_round'], 0)
        self.assertEqual(info['max_rounds'], 10)
        
    def test_statistics_tracking(self):
        """Test statistics collection."""
        stats = self.time_manager.get_current_month_stats()
        self.assertEqual(stats.month, 1)
        self.assertEqual(stats.year, 1)
        self.assertEqual(stats.total_actions, 0)


class TestMonthlyEvents(unittest.TestCase):
    """Test monthly event processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.time_manager = TimeManager()
        self.mock_agents = self._create_mock_agents()
        
    def _create_mock_agents(self) -> List[Mock]:
        """Create mock agents for testing."""
        agents = []
        for i in range(3):
            agent = Mock()
            agent.id = AgentID(f"agent_{i}")
            agent.action_budget = Mock()
            agent.internal_state = Mock()
            agent.internal_state.wealth = 1000.0
            agent.home = None
            agent.employment = None
            agent.update_internal_states = Mock()
            agents.append(agent)
        return agents
        
    def test_month_start(self):
        """Test month start processing."""
        self.time_manager.start_new_month(self.mock_agents)
        
        # Check that agent budgets were reset
        for agent in self.mock_agents:
            agent.action_budget.reset.assert_called_once()
            agent.update_internal_states.assert_called_once_with(delta_time=1)
            
        self.assertEqual(self.time_manager.current_round, 0)
        
    def test_action_round_advancement(self):
        """Test action round advancement."""
        self.time_manager.start_new_month(self.mock_agents)
        
        # Advance through rounds
        for round_num in range(1, 6):
            continues = self.time_manager.advance_action_round(self.mock_agents)
            self.assertTrue(continues)
            self.assertEqual(self.time_manager.current_round, round_num)
            
        # Complete the month
        for round_num in range(6, 11):
            continues = self.time_manager.advance_action_round(self.mock_agents)
            if round_num == 10:
                self.assertFalse(continues)
            else:
                self.assertTrue(continues)
                
    def test_rent_payment_processing(self):
        """Test rent payment processing."""
        # Create agent with housing
        agent = self.mock_agents[0]
        agent.home = Mock()
        agent.home.monthly_rent = 800.0
        agent.home.months_at_residence = 0
        
        self.time_manager._process_rent_payments([agent])
        
        # Check rent was deducted
        self.assertEqual(agent.internal_state.wealth, 200.0)  # 1000 - 800
        self.assertEqual(agent.home.months_at_residence, 1)
        
    def test_eviction_processing(self):
        """Test eviction for non-payment."""
        # Create agent with insufficient funds
        agent = self.mock_agents[0]
        agent.home = Mock()
        agent.home.monthly_rent = 1200.0  # More than agent's wealth
        agent.internal_state.wealth = 500.0
        agent.internal_state.stress = 0.3
        agent.internal_state.mood = 0.1
        
        self.time_manager._process_rent_payments([agent])
        
        # Check eviction occurred
        self.assertIsNone(agent.home)
        self.assertIsNone(agent.current_location)
        self.assertGreaterEqual(agent.internal_state.stress, 0.7)  # Increased
        self.assertLessEqual(agent.internal_state.mood, -0.2)  # Decreased
        
    def test_salary_payment_processing(self):
        """Test salary payment processing."""
        # Create employed agent
        agent = self.mock_agents[0]
        agent.employment = Mock()
        agent.employment.base_salary = 2000.0
        agent.employment.performance_history = Mock()
        agent.employment.performance_history.average_performance = 0.8
        agent.employment.performance_history.months_employed = 0
        agent.employment.performance_history.warnings_received = 0
        
        initial_wealth = agent.internal_state.wealth
        
        self.time_manager._process_salary_payments([agent])
        
        # Check salary was paid (2000 * 0.8 = 1600)
        expected_wealth = initial_wealth + 1600.0
        self.assertEqual(agent.internal_state.wealth, expected_wealth)
        self.assertEqual(agent.employment.performance_history.months_employed, 1)
        
    def test_job_loss_processing(self):
        """Test job loss due to poor performance."""
        # Create agent with poor performance
        agent = self.mock_agents[0]
        agent.employment = Mock()
        agent.employment.base_salary = 2000.0
        agent.employment.performance_history = Mock()
        agent.employment.performance_history.average_performance = 0.4
        agent.employment.performance_history.months_employed = 0
        agent.employment.performance_history.warnings_received = 3  # Threshold
        agent.internal_state.stress = 0.2
        agent.internal_state.mood = 0.1
        
        self.time_manager._process_salary_payments([agent])
        
        # Check job loss occurred
        self.assertIsNone(agent.employment)
        self.assertGreaterEqual(agent.internal_state.stress, 0.5)  # Increased
        self.assertLessEqual(agent.internal_state.mood, -0.1)  # Decreased


class TestSimulationIntegration(unittest.TestCase):
    """Test integration with the main Simulation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.city = self._create_mock_city()
        self.config = SimulationConfig(
            max_months=2,
            rounds_per_month=3,
            enable_logging=False
        )
        
    def _create_mock_city(self) -> City:
        """Create a minimal mock city."""
        plot = Plot(
            id=PlotID("test_plot"),
            location=Coordinate((0.0, 0.0)),
            district_id=DistrictID("test_district")
        )
        
        district = District(
            id=DistrictID("test_district"),
            name="Test District",
            wealth_level=DistrictWealth.WORKING_CLASS,
            plots=[plot]
        )
        
        return City(
            name="Test City",
            districts=[district]
        )
        
    def test_simulation_initialization(self):
        """Test simulation initialization with time manager."""
        simulation = Simulation(self.city, self.config)
        
        self.assertIsNotNone(simulation.time_manager)
        self.assertEqual(simulation.time_manager.max_rounds_per_month, 3)
        self.assertEqual(simulation.config.max_months, 2)
        
    def test_agent_addition(self):
        """Test adding agents to simulation."""
        simulation = Simulation(self.city, self.config)
        
        agent = Agent.create_random()
        simulation.add_agent(agent)
        
        self.assertIn(agent, simulation.agents)
        self.assertIn(agent.id, simulation.time_manager.active_agents)
        
    def test_agent_limit(self):
        """Test agent limit enforcement."""
        config = SimulationConfig(max_agents=2)
        simulation = Simulation(self.city, config)
        
        # Add agents up to limit
        for i in range(2):
            agent = Agent.create_random()
            simulation.add_agent(agent)
            
        # Try to add one more
        with self.assertRaises(ValueError):
            agent = Agent.create_random()
            simulation.add_agent(agent)
            
    def test_simulation_state(self):
        """Test simulation state reporting."""
        simulation = Simulation(self.city, self.config)
        
        # Add some agents
        for i in range(3):
            agent = Agent.create_random()
            simulation.add_agent(agent)
            
        state = simulation.get_simulation_state()

        self.assertEqual(state['total_agents'], 3)
        self.assertEqual(state['months_completed'], 0)
        self.assertFalse(state['is_running'])
        self.assertFalse(state['is_paused'])
        
    def test_agent_summary(self):
        """Test agent summary statistics."""
        simulation = Simulation(self.city, self.config)
        
        # Add agents
        for i in range(3):
            agent = Agent.create_random()
            simulation.add_agent(agent)
            
        summary = simulation.get_agent_summary()
        
        self.assertEqual(summary['total_agents'], 3)
        self.assertIn('average_wealth', summary)
        self.assertIn('employment_rate', summary)
        self.assertIn('housing_rate', summary)
        
    def test_custom_event_handlers(self):
        """Test custom event handler registration."""
        simulation = Simulation(self.city, self.config)
        
        handler_called = False
        
        def custom_handler(event_type, agents, time_manager):
            nonlocal handler_called
            handler_called = True
            
        simulation.add_event_handler(TimeEvent.MONTH_START, custom_handler)
        
        # Trigger event manually
        simulation.time_manager._trigger_event(TimeEvent.MONTH_START, [], simulation.time_manager)
        
        self.assertTrue(handler_called)


class TestStatisticsTracking(unittest.TestCase):
    """Test statistics tracking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.time_manager = TimeManager()
        
    def test_monthly_stats_creation(self):
        """Test monthly statistics creation."""
        stats = self.time_manager.get_current_month_stats()
        
        self.assertEqual(stats.month, 1)
        self.assertEqual(stats.year, 1)
        self.assertEqual(stats.total_actions, 0)
        self.assertEqual(stats.total_salaries_paid, 0.0)
        
    def test_stats_progression(self):
        """Test statistics progression across months."""
        # Simulate some activity
        self.time_manager.current_month_stats.total_actions = 50
        self.time_manager.current_month_stats.total_salaries_paid = 5000.0
        
        # End month to save stats
        self.time_manager.current_time.advance()
        self.time_manager.monthly_stats.append(self.time_manager.current_month_stats)
        
        # Start new month
        self.time_manager.current_month_stats = MonthlyStats(
            month=self.time_manager.current_time.month,
            year=self.time_manager.current_time.year
        )
        
        # Check historical stats
        historical = self.time_manager.get_monthly_statistics()
        self.assertEqual(len(historical), 1)
        self.assertEqual(historical[0].total_actions, 50)
        self.assertEqual(historical[0].total_salaries_paid, 5000.0)
        
        # Check new month stats are reset
        current = self.time_manager.get_current_month_stats()
        self.assertEqual(current.total_actions, 0)
        self.assertEqual(current.month, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2) 
