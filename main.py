import csv
import os
import sys
from datetime import datetime

import sdl2
import sdl2.ext
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

    @staticmethod
    def parse_file(filename: str) -> list:
        with open(file=filename, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")
            candles = []
            for row in reader:
                candles.append(Candle(row))

            return candles


BACKGROUND_COLOR = (39, 51, 56, 255)
RED = (224, 84, 84, 255)
GREEN = (43, 87, 72, 255)
BLACK = (0, 0, 0, 255)


def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Terminal", size=(800, 600))
    window.show()
    running = True
    render_flags = sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    renderer = sdl2.ext.Renderer(window, flags=render_flags)

    rect1 = sdl2.SDL_Rect(150, 200, 40, 40)
    rect2 = sdl2.SDL_Rect(100, 100, 20, 20)

    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        renderer.clear(BACKGROUND_COLOR)
        renderer.fill(
            [rect1, rect2],
            GREEN,
        )
        renderer.scale = (5.0, 5.0)
        renderer.draw_line([(20, 20), (300, 300)], BLACK)
        renderer.scale = (1.0, 1.0)
        renderer.present()

    sdl2.ext.quit()


def main():
    filename = os.getenv("FILENAME") or ""
    candles = Candle.parse_file(filename)
    for candle in candles:
        print(candle.info())


if __name__ == "__main__":
    sys.exit(run())
    # main()
