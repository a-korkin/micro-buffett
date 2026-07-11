import logging
import math
from datetime import datetime, timedelta

from pyray import (
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    draw_line_ex,
    draw_rectangle_v,
    draw_text,
    end_drawing,
    init_window,
    set_target_fps,
    window_should_close,
)
from raylib.colors import BLACK, WHITE

from models.candle import Candle

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (39, 51, 56, 255)
RED = (224, 84, 84, 255)
GREEN = (43, 87, 72, 255)
WIDTH = 1600
HEIGHT = 900
GAP = 20
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


class Graph:
    up_left: Vector2
    bottom_right: Vector2
    center: Vector2

    def __init__(self, up_left: Vector2, bottom_right: Vector2):
        self.up_left = up_left
        self.bottom_right = bottom_right
        self.center = Vector2(up_left.x, bottom_right.y)


# open: 3235.50, close: 3234.50, begin: 2026-07-09 06:59:00, end: 2026-07-09 06:59:59
# open: 3298.00, close: 3295.50, begin: 2026-07-09 08:46:00, end: 2026-07-09 08:46:59

# top: 3296, bottom: 3233


def _draw_scale_y(min: float, max: float):
    top = math.ceil(max)
    bottom = math.floor(min)

    length = float(HEIGHT - GAP * 3)
    count_mark = int(top - bottom)
    step_pxl = length / count_mark
    y = HEIGHT - GAP * 2
    thick = 2.0

    i = 0
    while y >= GAP:
        y -= step_pxl
        i += 1

        left = Vector2(GAP * 3 - 5, y)
        right = Vector2(GAP * 3 + 5, y)

        if i % 2 == 0:
            value = f"{float(bottom + i):.2f}"
            draw_text(value, GAP - 10, int(y - 4), 8, WHITE)

            left = Vector2(GAP * 3 - 7.5, y)
            right = Vector2(GAP * 3 + 7.5, y)

        draw_line_ex(left, right, thick, BLACK)


def _draw_scale_x(min_d: datetime, max_d: datetime):
    # TODO: проверять в каком формате интервалы (минуты, часы, дни)
    start = datetime.strptime(str(min_d), DATETIME_FMT) - timedelta(minutes=1)
    stop = datetime.strptime(str(max_d), DATETIME_FMT) + timedelta(minutes=1, seconds=1)

    length = float(WIDTH - GAP * 4)
    time_diff = (stop - start).total_seconds() / 60
    count_mark = int(time_diff)
    step_pxl = length / count_mark
    thick = 2.0
    x = GAP * 3

    y_pos = HEIGHT - GAP * 2
    while start < stop:
        start += timedelta(minutes=1)
        x += step_pxl

        up = Vector2(x, y_pos - 5)
        down = Vector2(x, y_pos + 5)

        if start.minute % 5 == 0:
            up = Vector2(x, y_pos - 7.5)
            down = Vector2(x, y_pos + 7.5)
            value = start.strftime("%H:%M")
            draw_text(value, int(x) - 10, y_pos + 10, 8, WHITE)

        draw_line_ex(up, down, thick, BLACK)


def _draw_axes(minc: Candle, maxc: Candle, graph: Graph):
    # TODO: установить центр координат
    thick = 2.0
    # y-axes
    draw_line_ex(
        graph.up_left,
        graph.center,
        thick,
        BLACK,
    )

    _min = min(minc.open, minc.close, minc.high, minc.low)
    _max = min(maxc.open, maxc.close, maxc.high, maxc.low)
    _draw_scale_y(min=float(_min), max=float(_max))

    # x-axes
    draw_line_ex(graph.center, graph.bottom_right, thick, BLACK)
    _min = minc.begin
    _max = maxc.end

    _draw_scale_x(min_d=_min, max_d=_max)


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


def draw_candles(candles: list[Candle]):
    pass


def run(candles: list[Candle]):
    minc, maxc = _candle_edges(candles)

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(60)

    graph = Graph(
        up_left=Vector2(GAP * 3, GAP - 10),
        bottom_right=Vector2(WIDTH - GAP, HEIGHT - GAP * 2),
    )

    pos = Vector2(200.0, 100.0)
    size = Vector2(30.0, 50.0)

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)
        _draw_axes(minc, maxc, graph)
        draw_rectangle_v(pos, size, GREEN)
        end_drawing()
    close_window()
