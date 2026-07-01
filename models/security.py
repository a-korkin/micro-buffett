from datetime import date
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Description:
    name: str
    title: str
    value: str
    type: str
    sort_order: int
    is_hidden: int
    precision: Optional[int] = None

    def __init__(self, obj: dict):
        self.name = obj["name"]
        self.title = obj["title"]
        self.value = obj["value"]
        self.type = obj["type"]
        self.sort_order = obj["sort_order"]
        self.is_hidden = obj["is_hidden"]
        self.precision = obj["precision"]

    def __str__(self) -> str:
        return f"name: {self.name}, title: {self.title}, value: {self.value}"


class BestSecurity:
    isin: str
    name: str
    issuevalue: int
    coupondate: date
    recorddate: Optional[date]
    startdate: Optional[date]
    initialfacevalue: float
    facevalue: float
    faceunit: str
    value: float
    valueprc: float
    value_rub: float
    secid: str
    primary_boardid: str
    info: dict[str, str]


class Security(Base):
    __tablename__ = "securities"
    secid: Mapped[str] = mapped_column(String(256), primary_key=True)
    description: Mapped[list[dict]] = mapped_column(ARRAY(JSONB))
    info: Mapped[dict] = mapped_column(JSONB)

    def __str__(self) -> str:
        return f"secid: {self.secid}"
