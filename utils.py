import os
from datetime import date
from typing import Optional

import csv
from models.candle import Candle


def parse_file(filename: str, _type: type) -> list:
    with open(file=filename, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return [_type(row) for row in reader]


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def save_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def optional_date(value) -> Optional[date]:
    if str(value) == "":
        return None
    try:
        return value
    except (ValueError, TypeError):
        return None


def get_candles() -> list[Candle]:
    filename = os.getenv("FILENAME") or ""
    candles = parse_file(filename, Candle)
    return candles
