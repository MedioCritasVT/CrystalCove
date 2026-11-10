import unittest
from observation.simulator import sample

class SimulatorTests(unittest.TestCase):
    def test_repeatable(self):
        self.assertEqual(sample(7), sample(7))
    def test_dropout_only_affects_temperature(self):
        readings = sample(22)
        self.assertEqual(readings[0].status, "unavailable")
        self.assertIsNone(readings[0].value)
        self.assertEqual(readings[1].status, "measured")
    def test_recovery(self):
        self.assertEqual(sample(26)[0].status, "measured")
    def test_invalid_step(self):
        with self.assertRaises(ValueError):
            sample(-1)

if __name__ == "__main__":
    unittest.main()
