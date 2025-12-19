from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Product Review API"
    api_v1_prefix: str = "/api/v1"

    # MongoDB settings
    mongodb_uri: str
    database_name: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    class Config:
        env_file = ".env"
