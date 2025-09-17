import unittest
from simulacra.simulation.simulation import Simulation, SimulationConfig
from simulacra.agents.agent import Agent
from simulacra.environment.city import City
from simulacra.environment.district import District
from simulacra.environment.plot import Plot
from simulacra.utils.types import PlotID, DistrictID, Coordinate, DistrictWealth


class TestSimulationControl(unittest.TestCase):
    def setUp(self):
        plot = Plot(id=PlotID('p1'), location=Coordinate((0.0, 0.0)), district_id=DistrictID('d1'))
        district = District(id=DistrictID('d1'), name='D1', wealth_level=DistrictWealth.WORKING_CLASS, plots=[plot])
        self.city = City(name='TestCity', districts=[district])

    def test_pause_resume_flags(self):
        sim = Simulation(self.city, SimulationConfig(max_months=1, rounds_per_month=1, enable_logging=False))
        sim.is_running = True
        sim.pause()
        self.assertTrue(sim.is_paused)
        sim.resume()
        self.assertFalse(sim.is_paused)

    def test_threaded_round(self):
        config = SimulationConfig(max_months=1, rounds_per_month=1, enable_logging=False, use_threading=True, num_threads=2)
        sim = Simulation(self.city, config)
        sim.add_agent(Agent.create_random())
        sim.is_running = True
        stats = sim.run_single_month()
        self.assertEqual(stats.month, 2)


if __name__ == '__main__':
    unittest.main()
