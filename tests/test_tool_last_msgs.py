import os
import unittest

from src.agent.tools.summary_last_x_msgs import load_chat_messages

class TestGetLatestMessages(unittest.TestCase):

    def setUp(self):
        self.folder_path = 'tests/data/chat_messages'
        self.assertTrue(os.path.exists(self.folder_path), "The folder data/chat_messages does not exist.")
        
        jsonl_files = [f for f in os.listdir(self.folder_path) if f.endswith('.jsonl')]
        self.assertGreater(len(jsonl_files), 0, "No JSONL files found in the data/chat_messages folder.")

    def test_get_latest_messages(self):
        test_cases = [0, 3, 10]
        
        for n in test_cases:
            latest_messages = load_chat_messages(self.folder_path, n)
            self.assertGreaterEqual(
                len(latest_messages), n, 
                f"Expected at most {n} messages, but got {len(latest_messages)}."
            )
    

if __name__ == '__main__':
    unittest.main()