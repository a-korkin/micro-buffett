from typing import cast

from sqlalchemy import insert, select

from models.coupon import Coupon

from .engine import engine


def add_coupon(coupon: Coupon):
    data = coupon.__dict__.copy()
    data.pop("_sa_instance_state", None)
    stmt = insert(Coupon).values(data)
    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()


def add_coupons(coupons: list[Coupon]):
    data = []
    for c in coupons:
        item = c.__dict__.copy()
        item.pop("_sa_instance_state", None)
        data.append(item)

    if len(data) > 0:
        stmt = insert(Coupon).values(data)
        with engine.connect() as connection:
            connection.execute(stmt)
            connection.commit()


def get_coupons() -> list[Coupon]:
    stmt = select(Coupon)
    with engine.connect() as connection:
        result = connection.execute(stmt).all()
        return cast("list[Coupon]", result)
