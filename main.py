import csv
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


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
            f"{prefix}open: {float(self.open):.2f}, close: {float(self.close):.2f}, "
            f"begin: {self.begin}, end: {self.end}, percent: {self.percent():>6.3f}, "
            f"avg: {self.average():.2f}{suffix}"
        )

    def percent(self) -> float:
        return round(
            ((float(self.close) - float(self.open)) / float(self.open)) * 100.0, 3
        )

    def average(self) -> float:
        return round((float(self.open) + float(self.close)) / 2.0, 2)

    @staticmethod
    def parse_file(filename: str) -> list:
        with open(file=filename, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")
            candles = []
            for row in reader:
                candles.append(Candle(row))

            return candles


def main():
    filename = os.getenv("FILENAME") or ""
    candles = Candle.parse_file(filename)
    for candle in candles:
        print(candle)


if __name__ == "__main__":
    main()
