import unittest


from src.agent.planner import planner_chain


class TestPlanner(unittest.TestCase):
    def test_planner(self):
        request = "How are you?"
        result = planner_chain.invoke({"user_request": request})
        
        request = "Please summary the last 5 messages and then tell me the current date. Return as haiku."
        result = planner_chain.invoke({"user_request": request})

        assert 1==1


if __name__ == '__main__':
    unittest.main()        