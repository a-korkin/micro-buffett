from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from utils import optional_date, safe_float, save_int

from .base import Base


class Coupon(Base):
    __tablename__ = "coupons"
    isin: Mapped[str] = mapped_column(String(256), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    issuevalue: Mapped[int] = mapped_column(BigInteger())
    coupondate: Mapped[date] = mapped_column(Date())
    recorddate: Mapped[Optional[date]] = mapped_column(Date())
    startdate: Mapped[Optional[date]] = mapped_column(Date())
    initialfacevalue: Mapped[float] = mapped_column(Float())
    facevalue: Mapped[float] = mapped_column(Float())
    faceunit: Mapped[str] = mapped_column(String(8))
    value: Mapped[float] = mapped_column(Float())
    valueprc: Mapped[float] = mapped_column(Float())
    value_rub: Mapped[float] = mapped_column(Float())
    secid: Mapped[str] = mapped_column(String(256))
    primary_boardid: Mapped[str] = mapped_column(String(8))

    def __init__(self, obj: dict):
        self.isin = obj["isin"]
        self.name = obj["name"]
        self.issuevalue = save_int(obj["issuevalue"])
        self.coupondate = obj["coupondate"]
        self.recorddate = optional_date(obj["recorddate"])
        self.startdate = optional_date(obj["startdate"])
        self.initialfacevalue = obj["initialfacevalue"]
        self.facevalue = obj["facevalue"]
        self.faceunit = obj["faceunit"]
        self.value = safe_float(obj["value"])
        self.valueprc = safe_float(obj["valueprc"])
        self.value_rub = safe_float(obj["value_rub"])
        self.secid = obj["secid"]
        self.primary_boardid = obj["primary_boardid"]

    def __str__(self) -> str:
        return (
            f"isin: {self.isin}, valueprc: {self.valueprc}, "
            f"couponsdate: {self.coupondate}, recorddate: {self.recorddate}"
        )
