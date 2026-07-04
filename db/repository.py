from typing import cast

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

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
