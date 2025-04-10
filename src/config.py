from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    envelopes_path: str
    stream_path: str
    logs_path: str

    signal_cli_path: str
    signal_cli_logs_path: str

    class Config:
        env_prefix = 'APP_CONFIG_'    

app_config = AppConfig()