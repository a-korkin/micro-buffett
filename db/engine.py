from sqlalchemy import create_engine

from config.settings import app_settings

engine = create_engine(app_settings.DB_URL)
