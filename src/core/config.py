import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic.env_settings import BaseSettings
from pydantic.networks import PostgresDsn

from core.logger import LOGGING

load_dotenv('.env')

logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.environ['PROJECT_NAME']
PROJECT_HOST = os.environ['PROJECT_HOST']
PROJECT_PORT = int(os.environ['PROJECT_PORT'])


class AppSettings(BaseSettings):
    app_title: str = "LibraryApp"
    database_dsn: PostgresDsn
    secret: str

    class Config:
        env_file = '.env'


app_settings = AppSettings()
