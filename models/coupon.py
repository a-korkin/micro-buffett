from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Coupon(Base):
    __tablename__ = "coupons"
    isin: Mapped[str] = mapped_column(String(256), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    issuevalue: Mapped[int] = mapped_column(Integer())
    coupondate: Mapped[date] = mapped_column(Date())
    recorddate: Mapped[date] = mapped_column(Date())
    startdate: Mapped[date] = mapped_column(Date())
    initialfacevalue: Mapped[int] = mapped_column(Integer())
    facevalue: Mapped[int] = mapped_column(Integer())
    faceunit: Mapped[str] = mapped_column(String(8))
    value: Mapped[float] = mapped_column(Float())
    valueprc: Mapped[float] = mapped_column(Float())
    value_rub: Mapped[float] = mapped_column(Float())
    secid: Mapped[str] = mapped_column(String(256))
    primary_boardid: Mapped[str] = mapped_column(String(8))
