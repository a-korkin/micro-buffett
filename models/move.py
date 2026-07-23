import enum
import uuid
from typing import Optional

from sqlalchemy import UUID, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Operation(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Move(Base):
    __tablename__ = "moves"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candle_id: Mapped[UUID] = mapped_column(ForeignKey("candles.id"))
    previous_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("moves.id"))
    current: Mapped[float] = mapped_column(Float())
    total: Mapped[float] = mapped_column(Float())
    operation: Mapped[Operation] = mapped_column(Enum(Operation, name="operations"))

    def __init__(
        self,
        candle_id: UUID,
        previous_id: Optional[UUID],
        current: float,
        total: float,
        operation: Operation,
    ):
        self.candle_id = candle_id
        self.previous_id = previous_id
        self.current = current
        self.total = total
        self.operation = operation
