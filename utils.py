from datetime import date
from typing import Optional


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
