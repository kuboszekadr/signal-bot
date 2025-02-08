import unittest

from langchain_openai import AzureChatOpenAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.models.azure_openai import azure_open_ai_config

class TestAzureOpenAIConfig(unittest.TestCase):

    def setUp(self):
        self.llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())

    def test_config(self):

        response = self.llm.invoke("How are you today?")
        msg = response.content
        self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()