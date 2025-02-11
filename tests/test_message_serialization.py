import unittest
import json
import glob

from src.models.signal import Envelope

class TestEnvelope(unittest.TestCase):
    def test_envelope_serialization(self):
        example_files = glob.glob('./tests/example_msgs/*.json')
        for file_path in example_files:
            with open(file_path, 'r') as file:
                data = json.load(file)
                try:
                    envelope = Envelope(**data['envelope'])
                except Exception as e:
                    self.fail(f"Failed to serialize envelope: {e}\n{file_path}")
        
if __name__ == '__main__':
    unittest.main()