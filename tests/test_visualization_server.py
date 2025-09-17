import unittest
from simulacra.simulation.simulation import Simulation, SimulationConfig
from simulacra.environment.city import City
from simulacra.environment.district import District
from simulacra.environment.plot import Plot
from simulacra.utils.types import PlotID, DistrictID, Coordinate, DistrictWealth
from simulacra.analytics.metrics import MetricsCollector
from simulacra.visualization.data_streamer import DataStreamer
from simulacra.visualization.visualization_server import VisualizationServer


class TestSimulationControlAPI(unittest.TestCase):
    def setUp(self):
        plot = Plot(id=PlotID('p1'), location=Coordinate((0.0, 0.0)), district_id=DistrictID('d1'))
        district = District(id=DistrictID('d1'), name='D1', wealth_level=DistrictWealth.WORKING_CLASS, plots=[plot])
        city = City(name='TestCity', districts=[district])
        self.simulation = Simulation(city, SimulationConfig(max_months=1, rounds_per_month=1, enable_logging=False))
        self.simulation.is_running = True
        streamer = DataStreamer(self.simulation, MetricsCollector())
        self.server = VisualizationServer(streamer)
        self.client = self.server.app.test_client()

    def test_pause_resume_and_stop(self):
        resp = self.client.post('/api/simulation-control', json={'action': 'pause'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.simulation.is_paused)
        self.assertEqual(resp.get_json()['status'], 'paused')

        resp = self.client.post('/api/simulation-control', json={'action': 'resume'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.simulation.is_paused)
        self.assertEqual(resp.get_json()['status'], 'running')

        resp = self.client.post('/api/simulation-control', json={'action': 'stop'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.simulation.is_running)
        self.assertEqual(resp.get_json()['status'], 'stopped')


if __name__ == '__main__':
    unittest.main()
