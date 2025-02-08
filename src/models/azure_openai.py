from pydantic_settings import BaseSettings

class AzureOpenAiConfig(BaseSettings):
    deployment_name: str
    openai_api_version: str
    azure_endpoint: str
    openai_api_key: str

    class Config:
        env_prefix = 'AZURE_OPENAI_'

azure_open_ai_config = AzureOpenAiConfig()