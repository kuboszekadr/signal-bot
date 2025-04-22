import unittest

from src.agent.planner import Plan
from src.agent.agent_20 import execute_plan_step, State, agent

plan = Plan(
    steps=[
        {
            "tool_name": "get_current_date",
            "reason": "To retrieve the current date that will be included in the haiku.",
            "step_number": 1,
        },
        {
            "tool_name": "simple_request",
            "reason": "To create haiku refering to current date",
            "step_number": 2,
        },
    ]
)

state = {
    "chat_id": "12345",
    "context": "User is asking for a haiku.",
    "user_request": "Return a haiku based on the current date",
    "plan": plan,
    "current_step": 0,
}
state = State(**state)

class TestPlannerExecutor(unittest.TestCase):
    def test_step_executor(self):
        # Execute the first step of the plan
        result = execute_plan_step(state)
        self.assertEqual(result['current_step'], 1)

    def test_plan_executor(self):
        result = agent.invoke(state)
        self.assertEqual(result['current_step'], 2)


if __name__ == '__main__':
    unittest.main()        