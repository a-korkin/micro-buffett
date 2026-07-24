import enum
import uuid
from typing import Optional

from sqlalchemy import UUID, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.candle import Candle

from .base import Base


class Operation(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Move(Base):
    __tablename__ = "moves"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candle_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candles.id")
    )
    candle: Mapped["Candle"] = relationship("Candle", foreign_keys="[Move.candle_id]")

    previous_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("moves.id"))
    summ: Mapped[float] = mapped_column(Float())
    remain: Mapped[float] = mapped_column(Float())
    count: Mapped[int] = mapped_column(Integer())
    price: Mapped[float] = mapped_column(Float())
    operation: Mapped[Operation] = mapped_column(Enum(Operation, name="operations"))
    sprint_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    def __init__(
        self,
        candle_id: UUID,
        previous_id: Optional[UUID],
        summ: float,
        remain: float,
        count: int,
        price: float,
        operation: Operation,
        sprint_id: uuid.UUID,
    ):
        self.candle_id = candle_id
        self.previous_id = previous_id
        self.summ = summ
        self.remain = remain
        self.count = count
        self.price = price
        self.operation = operation
        self.sprint_id = sprint_id

    def __str__(self) -> str:
        return (
            f"summ: {self.summ:.2f}, remain: {self.remain:.2f}, "
            f"count: {self.count}, price: {self.price:.2f}, {self.operation}"
        )
