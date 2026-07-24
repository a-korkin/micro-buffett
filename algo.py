import math
from typing import Optional
from uuid import UUID

from db import repository
from models.candle import Candle
from models.move import Move, Operation

COMMISSION = 0.0005


def make_move(
    candle: Candle,
    last_move: Optional[Move],
    sprint_id: UUID,
    balance: float,
) -> Move:
    previous_id = None
    operation = Operation.BUY

    if last_move:
        previous_id = last_move.id
        if last_move.operation == Operation.BUY:
            operation = Operation.SELL
        else:
            operation = Operation.BUY

    average = candle.average()
    price = round(average + average * COMMISSION, 2)
    count = 0
    summ = 0.0
    remain = 0.0

    if operation == Operation.BUY:
        count = math.floor(balance / price)
        summ = price * count
        remain = balance - summ
    else:
        if last_move:
            count = last_move.count
            summ = price * count
            remain = balance + summ

    move = Move(
        candle_id=candle.id,
        previous_id=previous_id,
        summ=round(summ, 2),
        remain=round(remain, 2),
        count=count,
        price=price,
        operation=operation,
        sprint_id=sprint_id,
    )

    return repository.add_move(move)


def replay_moves(sprint_id: UUID) -> list[tuple[Move, Candle]]:
    return repository.get_moves(sprint_id)
