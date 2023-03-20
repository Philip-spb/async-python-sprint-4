import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic.env_settings import BaseSettings
from pydantic.networks import PostgresDsn

from core.logger import LOGGING

load_dotenv('.env')

logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str = "LibraryApp"
    project_name: str
    project_host: str
    project_port: int
    database_dsn: PostgresDsn
    secret: str
    black_list: list

    class Config:
        env_file = '.env'


app_settings = AppSettings()
