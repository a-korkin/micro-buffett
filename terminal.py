import logging
import math

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
    top = math.ceil(max)
    bottom = math.floor(min)

    length = float(HEIGHT - GAP * 2)
    count_mark = int(top - bottom)
    print(length, count_mark)

    # length = float(HEIGHT - GAP * 2)
    # step = length / (float(max) - float(min))
    # y = HEIGHT - GAP
    # thick = 2.0
    # while y >= GAP:
    #     y -= step
    #     left = Vector2(GAP - 7.5, y)
    #     right = Vector2(GAP + 7.5, y)
    #     draw_line_ex(left, right, thick, BLACK)


def _draw_axes(minc: Candle, maxc: Candle):
    upper_left = Vector2(GAP, GAP)
    lower_left = Vector2(GAP, HEIGHT - GAP)
    lower_right = Vector2(WIDTH - GAP, HEIGHT - GAP)
    thick = 2.0

    # y-axes
    draw_line_ex(upper_left, lower_left, thick, BLACK)

    _min = min(minc.open, minc.close, minc.high, minc.low)
    _max = min(maxc.open, maxc.close, maxc.high, maxc.low)
    _draw_scale_y(min=float(_min), max=float(_max))

    # x-axes
    draw_line_ex(lower_left, lower_right, thick, BLACK)


def _candle_edges(candles: list[Candle]) -> tuple[Candle, Candle]:
    init = candles[0]
    minc = Candle(init.__dict__)
    maxc = Candle(init.__dict__)
    for candle in candles[1:]:
        if candle.open < minc.open:
            minc.open = candle.open
        if candle.close < minc.close:
            minc.close = candle.close
        if candle.high < minc.high:
            minc.high = candle.high
        if candle.low < minc.low:
            minc.low = candle.low
        if candle.value < minc.value:
            minc.value = candle.value
        if candle.volume < minc.volume:
            minc.volume = candle.volume
        if candle.begin < minc.begin:
            minc.begin = candle.begin
        if candle.end < minc.end:
            minc.end = candle.end

        if candle.open > maxc.open:
            maxc.open = candle.open
        if candle.close > maxc.close:
            maxc.close = candle.close
        if candle.high > maxc.high:
            maxc.high = candle.high
        if candle.low > maxc.low:
            maxc.low = candle.low
        if candle.value > maxc.value:
            maxc.value = candle.value
        if candle.volume > maxc.volume:
            maxc.volume = candle.volume
        if candle.begin > maxc.begin:
            maxc.begin = candle.begin
        if candle.end > maxc.end:
            maxc.end = candle.end

    return minc, maxc


def run(candles: list[Candle]):
    minc, maxc = _candle_edges(candles)

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(60)

    pos = Vector2(200.0, 100.0)
    size = Vector2(30.0, 50.0)

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)
        _draw_axes(minc, maxc)
        draw_rectangle_v(pos, size, GREEN)
        end_drawing()
    close_window()
