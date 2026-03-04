from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONOGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "combats"

    class Config:
        env_file = ".env"

settings = Settings()