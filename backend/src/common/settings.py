from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding='utf-8')
    bot_token: SecretStr
    db_url: str


config = Settings()
