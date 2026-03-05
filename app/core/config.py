from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONOGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "combats"
    MONSTERS_API_BASE_URL: str = None
    MONSTERS_API_PORT: str = None

    class Config:
        env_file = ".env"

settings = Settings()