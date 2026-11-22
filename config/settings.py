from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openrouter"

    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()