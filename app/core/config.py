from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    TMDB_API_KEY: str = ""
    class Config:
        env_file = ".env"


settings = Settings()