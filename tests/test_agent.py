import unittest
from src.agent.agent import invoke

class TestAgent(unittest.TestCase):

    def test_agent_tool_selection(self):
        user_request = "Summarize the last 5 messages."
        print(invoke(user_request))

    def test_agent_tool_selection_with_unknown_request(self):
        user_request = "Jaka jest dziś pogoda?"
        print(invoke(user_request))

    def test_agent_tool_selection_with_empty_request(self):
        user_request = ""
        print(invoke(user_request))

    def test_agent_summary_invoke(self):
        user_request = "Summarize the last 5 messages."
        chat_id = "932753e4-8c0a-4dde-87aa-a116b0c4949a" 
        print(invoke(user_request, chat_id))

if __name__ == '__main__':
    unittest.main()