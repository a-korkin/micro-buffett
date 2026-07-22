import uuid
from typing import Optional

from sqlalchemy import UUID, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Move(Base):
    __tablename__ = "moves"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candle_id: Mapped[UUID] = mapped_column(ForeignKey("candles.id"))
    previous_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("moves.id"))
    current: Mapped[float] = mapped_column(Float())
    total: Mapped[float] = mapped_column(Float())
