from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./kp_astrology.sqlite3"
    ollama_url: str = "http://localhost:11434/api/generate"
    lm_studio_url: str = "http://localhost:1234/v1/chat/completions"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
