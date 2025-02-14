import unittest
from src.agent.tools.simple import simple_request_chain

class TestSimpleRequest(unittest.TestCase):

    def test_simple_request_with_context(self):
        input_message = "Hello, how are you?"
        context = "The user is asking about your well-being."
        response = simple_request_chain.invoke({
            'user_message': input_message,
            'context': context
        })

        self.assertIsInstance(response, str)

    def test_simple_request_without_context(self):
        input_message = "Tell me a joke."
        response = simple_request_chain(input_message)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_simple_request_empty_input(self):
        input_message = ""
        response = simple_request_chain(input_message)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_simple_request_none_input(self):
        input_message = None
        with self.assertRaises(TypeError):
            simple_request_chain(input_message)

if __name__ == '__main__':
    unittest.main()