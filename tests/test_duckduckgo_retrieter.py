import unittest
from src.agent.tools.web_search import web_search, web_search_tool
from typing import List

class TestWebSearch(unittest.TestCase):

    def test_search_results_not_empty(self):
        query = "Python programming"
        results = web_search(query)
        self.assertTrue(
            len(results) > 0, 
            "Search results should not be empty"
        )

    def test_search_results_contains_query(self):
        query = "Python programming"
        results = web_search(query)
        self.assertTrue(
            any(query.lower() in result.snippet.lower() for result in results), 
            "Search results should contain the query"
        )

    def test_web_search_tool(self):
        user_message = "What is a date today? I would like to see weather forecast for tomorrow."
        search_results = web_search_tool.invoke(user_message)

        self.assertIsInstance(search_results, str)


if __name__ == '__main__':
    unittest.main()