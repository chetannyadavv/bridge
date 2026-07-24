import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://bridge:bridge@localhost:5432/bridge"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]

    model_config = {"env_prefix": "BRIDGE_"}


settings = Settings()
