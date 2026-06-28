from datetime import date

from sqlalchemy import BigInteger, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from utils import safe_float

from .base import Base


class Coupon(Base):
    __tablename__ = "coupons"
    isin: Mapped[str] = mapped_column(String(256), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    issuevalue: Mapped[int] = mapped_column(BigInteger())
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

    def __init__(self, obj: dict):
        self.isin = obj["isin"]
        self.name = obj["name"]
        self.issuevalue = obj["issuevalue"]
        self.coupondate = obj["coupondate"]
        self.recorddate = obj["recorddate"]
        self.startdate = obj["startdate"]
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
