import csv
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from terminal import run

load_dotenv()


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class Candle:
    open: float
    close: float
    high: float
    low: float
    value: float
    volume: int
    begin: datetime
    end: datetime

    def __init__(self, obj: dict):
        self.open = obj["open"]
        self.close = obj["close"]
        self.high = obj["high"]
        self.low = obj["low"]
        self.value = obj["value"]
        self.volume = obj["volume"]
        self.begin = obj["begin"]
        self.end = obj["end"]

    def __str__(self) -> str:
        return (
            f"open: {float(self.open):.2f}, close: {float(self.close):.2f}, "
            f"begin: {self.begin}, end: {self.end}, percent: {self.percent():>6.3f}, "
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


class Coupon:
    isin: str
    name: str
    issuevalue: float
    coupondate: datetime
    recorddate: datetime
    startdate: datetime
    initialfacevalue: float
    facevalue: float
    faceunit: str
    value: float
    valueprc: float
    value_rub: float
    secid: str
    primary_boardid: str

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
        self.value = obj["value"]
        self.valueprc = safe_float(obj["valueprc"])
        self.value_rub = obj["value_rub"]
        self.secid = obj["secid"]
        self.primary_boardid = obj["primary_boardid"]

    def __str__(self) -> str:
        return f"isin: {self.isin}, valueprc: {self.valueprc}"


def parse_file(filename: str, _type: type) -> list:
    with open(file=filename, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return [_type(row) for row in reader]


def candles_show():
    filename = os.getenv("FILENAME") or ""
    candles = parse_file(filename, Candle)
    min_open: Candle = min(candles, key=lambda c: c.open)
    max_open: Candle = max(candles, key=lambda c: c.open)
    max_percent: Candle = max(candles, key=lambda c: c.percent())
    print(min_open)
    print(max_open)
    print(max_percent)
    # for candle in candles:
    #     print(candle.info())


def coupons_show():
    filename = os.getenv("FILENAME") or ""
    coupons = parse_file(filename, Coupon)
    for coupon in coupons:
        print(coupon)
    max_percent: Coupon = max(coupons, key=lambda c: float(c.valueprc))
    print("===================================================")
    print("MAX =>", max_percent)


def main():
    # candles_show()
    coupons_show()


if __name__ == "__main__":
    # sys.exit(run())
    main()
