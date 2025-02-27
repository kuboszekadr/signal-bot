import unittest
from src.agent.agent import invoke

class TestAgent(unittest.TestCase):

        def test_agent_weather_multilingual(self):
            """Test weather query in different languages"""
            test_cases = [
                ("Wie ist das Wetter in Berlin?", "berlin"),  # German
                ("Quel temps fait-il à Paris?", "paris"),     # French
                ("¿Qué tiempo hace en Madrid?", "madrid"),    # Spanish
            ]
            
            for query, city in test_cases:
                with self.subTest(query=query):
                    response = invoke(query, "test-weather-2")
                    self.assertIsNotNone(response)
                    self.assertTrue(city.lower() in response.lower())

if __name__ == '__main__':
    unittest.main()