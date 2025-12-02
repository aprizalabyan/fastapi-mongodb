from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Base Project"
    api_v1_prefix: str = "/api/v1"

    # MongoDB settings
    mongodb_uri: str
    database_name: str = "api-test-v2"

    class Config:
        env_file = ".env"
