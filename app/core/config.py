from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Base Project"
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
