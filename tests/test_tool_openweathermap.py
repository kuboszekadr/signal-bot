import unittest
from src.agent.agent import invoke

class TestAgentOpenWeatherMap(unittest.TestCase):

        def test_agent_weather_multilingual(self):
            """Test weather query in different languages"""
            test_cases = [
                ("Wie ist das Wetter in Berlin?", "berlin"),  # German
                ("Quel temps fait-il à Paris?", "paris"),     # French
                ("¿Qué tiempo hace en Madrid?", "madrid"),    # Spanish
                ("What is the forecast for semmering between 01.03 and 02.03.2025?", "semmering"),    # Spanish
            ]
            
            for query, city in test_cases:
                    response = invoke(query)
                    self.assertIsNotNone(response)
                    self.assertTrue(city.lower() in response.content.lower())

if __name__ == '__main__':
    unittest.main()