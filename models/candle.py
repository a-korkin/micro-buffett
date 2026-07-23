import uuid
from datetime import datetime

from sqlalchemy import UUID, BigInteger, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Vector2:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Candle(Base):
    __tablename__ = "candles"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    secid: Mapped[str] = mapped_column(String(256))
    open: Mapped[float] = mapped_column(Float())
    close: Mapped[float] = mapped_column(Float())
    high: Mapped[float] = mapped_column(Float())
    low: Mapped[float] = mapped_column(Float())
    value: Mapped[float] = mapped_column(Float())
    volume: Mapped[int] = mapped_column(BigInteger())
    begin: Mapped[datetime] = mapped_column(DateTime())
    end: Mapped[datetime] = mapped_column(DateTime())
    position: Vector2 = Vector2(0.0, 0.0)
    size: Vector2 = Vector2(0.0, 0.0)

    def __init__(self, obj: dict):
        self.id = obj.get("id", uuid.uuid4())
        self.secid = obj["secid"]
        self.open = obj["open"]
        self.close = obj["close"]
        self.high = obj["high"]
        self.low = obj["low"]
        self.value = obj["value"]
        self.volume = obj["volume"]
        self.begin = obj["begin"]
        self.end = obj["end"]
        self.position = Vector2(0.0, 0.0)
        self.size = Vector2(0.0, 0.0)

    def __str__(self) -> str:
        return (
            f"secid: {self.secid}, open: {float(self.open):.2f}, close: {float(self.close):.2f}, "
            f"begin: {self.begin}, percent: {self.percent():>6.3f}, "
            f"avg: {self.average():.2f}"
        )

    def percent(self) -> float:
        return round(
            ((float(self.close) - float(self.open)) / float(self.open)) * 100.0, 3
        )

    def average(self) -> float:
        return round((float(self.open) + float(self.close)) / 2.0, 2)

    def info(self) -> str:
        prefix = ""
        suffix = "\033[0m"
        if self.open < self.close:
            prefix = "\033[32m"
        elif self.open > self.close:
            prefix = "\033[31m"
        else:
            prefix = ""
            suffix = ""

        return (
            f"{prefix}begin: {self.begin}, percent: {self.percent():>6.3f}, "
            f"avg: {self.average():.2f}{suffix}"
        )

    def set_coordinates(self, x: float, y: float, w: float, h: float):
        self.position = Vector2(x, y)
        self.size = Vector2(w, h)
