import logging

from pyray import (
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    draw_line_ex,
    draw_rectangle_v,
    end_drawing,
    init_window,
    set_target_fps,
    window_should_close,
)
from raylib.colors import BLACK

from models.candle import Candle

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (39, 51, 56, 255)
RED = (224, 84, 84, 255)
GREEN = (43, 87, 72, 255)
WIDTH = 800
HEIGHT = 600
GAP = 20


def _draw_scale_y(min: float, max: float):
    length = float(HEIGHT - GAP * 2)
    step = length / (max - min)
    y = HEIGHT - GAP
    thick = 2.0
    while y >= GAP:
        y -= step
        left = Vector2(GAP - 7.5, y)
        right = Vector2(GAP + 7.5, y)
        draw_line_ex(left, right, thick, BLACK)


def _draw_axes():
    upper_left = Vector2(GAP, GAP)
    lower_left = Vector2(GAP, HEIGHT - GAP)
    lower_right = Vector2(WIDTH - GAP, HEIGHT - GAP)
    thick = 2.0

    # y-axes
    draw_line_ex(upper_left, lower_left, thick, BLACK)
    _draw_scale_y(212.0, 230.0)
    # x-axes
    draw_line_ex(lower_left, lower_right, thick, BLACK)

    # open: float
    # close: float
    # high: float
    # low: float
    # value: float
    # volume: int
    # begin: datetime
    # end: datetime


def _candle_edges(candles: list[Candle]) -> tuple[Candle, Candle]:
    init = candles[0]
    min = Candle(init.__dict__)
    max = Candle(init.__dict__)
    for candle in candles[1:]:
        if candle.open < min.open:
            min.open = candle.open
        if candle.close < min.close:
            min.close = candle.close
        if candle.high < min.high:
            min.high = candle.high
        if candle.low < min.low:
            min.low = candle.low
        if candle.value < min.value:
            min.value = candle.value
        if candle.volume < min.volume:
            min.volume = candle.volume
        if candle.begin < min.begin:
            min.begin = candle.begin
        if candle.end < min.end:
            min.end = candle.end

        if candle.open > max.open:
            max.open = candle.open
        if candle.close > max.close:
            max.close = candle.close
        if candle.high > max.high:
            max.high = candle.high
        if candle.low > max.low:
            max.low = candle.low
        if candle.value > max.value:
            max.value = candle.value
        if candle.volume > max.volume:
            max.volume = candle.volume
        if candle.begin > max.begin:
            max.begin = candle.begin
        if candle.end > max.end:
            max.end = candle.end

    return min, max


def run(candles: list[Candle]):
    min, max = _candle_edges(candles)
    print(min)
    print(max)
    return

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(60)

    pos = Vector2(200.0, 100.0)
    size = Vector2(30.0, 50.0)

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)
        _draw_axes()
        draw_rectangle_v(pos, size, GREEN)
        end_drawing()
    close_window()
