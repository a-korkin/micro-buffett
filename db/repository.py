from datetime import datetime
from enum import Enum
from typing import cast

from sqlalchemy import and_, func, select, text
from sqlalchemy.dialects.postgresql import insert

from models.candle import Candle
from models.coupon import Coupon
from models.security import BestSecurity, Security

from .engine import engine


def add_coupons(coupons: list[Coupon]):
    data = []
    for c in coupons:
        item = c.__dict__.copy()
        item.pop("_sa_instance_state", None)
        data.append(item)

    if len(data) > 0:
        stmt = insert(Coupon).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["isin"],
            set_=dict(
                name=stmt.excluded.name,
                issuevalue=stmt.excluded.issuevalue,
                coupondate=stmt.excluded.coupondate,
                recorddate=stmt.excluded.recorddate,
                startdate=stmt.excluded.startdate,
                initialfacevalue=stmt.excluded.initialfacevalue,
                facevalue=stmt.excluded.facevalue,
                faceunit=stmt.excluded.faceunit,
                value=stmt.excluded.value,
                valueprc=stmt.excluded.valueprc,
                value_rub=stmt.excluded.value_rub,
            ),
        )

        with engine.connect() as connection:
            connection.execute(stmt)
            connection.commit()


def get_coupons() -> list[Coupon]:
    stmt = select(Coupon)
    with engine.connect() as connection:
        result = connection.execute(stmt).all()
        return cast("list[Coupon]", result)


def get_coupon(secid: str) -> Coupon:
    stmt = select(Coupon).where(Coupon.isin == secid)
    with engine.connect() as connection:
        result = connection.execute(stmt).first()
        return cast("Coupon", result)


def add_security_description(security: Security):
    data = security.__dict__.copy()
    data.pop("_sa_instance_state", None)
    stmt = insert(Security).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["secid"],
        set_=dict(
            description=stmt.excluded.description,
            info=stmt.excluded.info,
        ),
    )

    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()


def get_security_descriptions() -> list[Security]:
    stmt = select(Security)
    with engine.connect() as connection:
        result = connection.execute(stmt).all()
        return cast("list[Security]", result)


def get_best_choices(min_percent: float = 25.0) -> list[BestSecurity]:
    condition = (
        '{"ISQUALIFIEDINVESTORS": "0", "HASPROSPECTUS": "1", "COUPONFREQUENCY": "12"}'
    )
    sql = text(f"""
select b.*, a.info
from public.securities as a
inner join public.coupons as b on b.isin = a.secid
where a.info @> '{condition}'::jsonb
    and b.valueprc >= {min_percent}
order by b.valueprc desc;
    """)
    with engine.connect() as connection:
        result = connection.execute(sql).all()
        return cast("list[BestSecurity]", result)


def add_candle(candle: Candle):
    item = candle.__dict__.copy()
    item.pop("_sa_instance_state", None)
    item.pop("position", None)
    item.pop("size", None)

    stmt = insert(Candle).values(item)
    stmt = stmt.on_conflict_do_update(
        index_elements=["secid", "begin", "end"],
        set_=dict(
            open=stmt.excluded.open,
            close=stmt.excluded.close,
            high=stmt.excluded.high,
            low=stmt.excluded.low,
            volume=stmt.excluded.volume,
        ),
    )

    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()


def add_candles(candles: list[Candle]):
    data = []
    for c in candles:
        item = c.__dict__.copy()
        item.pop("_sa_instance_state", None)
        item.pop("position", None)
        item.pop("size", None)
        data.append(item)

    if len(data) > 0:
        stmt = insert(Candle).values(data)
        # stmt = stmt.on_conflict_do_update(
        #     index_elements=["secid", "begin", "end"],
        #     set_=dict(
        #         open=stmt.excluded.open,
        #         close=stmt.excluded.close,
        #         high=stmt.excluded.high,
        #         low=stmt.excluded.low,
        #         volume=stmt.excluded.volume,
        #     ),
        # )

        with engine.connect() as connection:
            connection.execute(stmt)
            connection.commit()


class Interval(Enum):
    min_1 = "1 minutes"
    min_15 = "15 minutes"
    hour_1 = "1 hours"


def get_candles(
    secid: str,
    period: datetime,
    interval: Interval,
    limit: int,
    offset: int,
) -> list[Candle]:
    if interval == Interval.min_1:
        sql = text(f"""
select 
    "secid", "open", "close", "high", "low", "value", "volume", "begin", "end"
from public.candles
where "secid" = '{secid}'
    and "begin"::date = '{period}'::date
order by "begin"
offset {offset}
limit {limit};""")
    else:
        sql = text(f"""
select 
    a."secid", round(avg(a."open")::numeric, 2) as "open", round(avg(a."close")::numeric, 2) as "close", 
    round(avg(a."high")::numeric, 2) as "high", round(avg(a."low")::numeric, 2) as "low", 
    round(avg(a."value")::numeric, 2) as "value", avg(a."volume") as "volume", 
	a."begin", a."end"
from
(
	select 
		"secid", "open", "close", "high", "low", "value", "volume", 
		date_bin('{interval.value}', "begin", "begin"::date) as "begin",
		date_bin('{interval.value}', "begin", "begin"::date) + '{interval.value} - 1 seconds'::interval as "end"
	from public.candles
	where "secid" = '{secid}'
) as a
group by a."secid", a."begin", a."end"
order by a."begin"
offset {offset}
limit {limit};""")

    with engine.connect() as connection:
        return [
            Candle(row._mapping)
            for row in cast("list[Candle]", connection.execute(sql).all())
        ]
