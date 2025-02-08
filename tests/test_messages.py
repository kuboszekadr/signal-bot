import unittest
import json
from models.signal import Envelope

class TestEnvelope(unittest.TestCase):
    def test_envelope_serialization(self):
        with open('./tests/example_msgs/text_message.json', 'r') as file:
            data = json.load(file)
        
        envelope = Envelope(**data['envelope'])
        
if __name__ == '__main__':
    unittest.main()