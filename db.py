import os

from sqlalchemy import create_engine, text

from config.settings import settings

# engine = create_engine(os.getenv("DB_URL"))


def execute():
    print(settings.DB_URL)
    # with engine.connect() as connection:
    #     result = connection.execute(text("select * from coupons"))
    #     for row in result:
    #         print(row)
