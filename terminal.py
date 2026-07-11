import logging
import math
from datetime import datetime, timedelta

from pyray import (
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    draw_line_ex,
    draw_rectangle_lines_ex,
    draw_rectangle_rec,
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

FPS = 60
BACKGROUND_COLOR = (39, 51, 56, 255)
RED = (224, 84, 84, 255)
GREEN = (43, 87, 72, 255)
WIDTH = 1024  # 1600
HEIGHT = 768  # 900
GAP = 20
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


class Scale:
    title: str
    position: Vector2
    index: int

    def __init__(self, title: str, position: Vector2, index: int):
        self.title = title
        self.position = position
        self.index = index


class Axe:
    start_point: Vector2
    end_point: Vector2
    max_value: float
    min_value: float

    scales: list[Scale]

    def __init__(
        self,
        start_point: Vector2,
        end_point: Vector2,
        minc: Candle,
        maxc: Candle,
    ):
        self.start_point = start_point
        self.end_point = end_point

        _min = float(min(minc.open, minc.close, minc.high, minc.low))
        _max = float(max(maxc.open, maxc.close, maxc.high, maxc.low))

        self.max_value = float(math.ceil(_max))
        self.min_value = float(math.floor(_min))

        self.scales = []


class Graph:
    up_left: Vector2
    bottom_right: Vector2
    center: Vector2

    axe_x: Axe
    axe_y: Axe

    candles: list[Candle]
    minc: Candle
    maxc: Candle

    thick: float = 2.0

    max_y: float
    min_y: float

    start: datetime
    stop: datetime

    step_y: float
    step_x: float

    def __init__(self, up_left: Vector2, bottom_right: Vector2):
        self.up_left = up_left
        self.bottom_right = bottom_right
        self.center = Vector2(up_left.x, bottom_right.y)
        self.start = datetime.today()
        self.stop = datetime.today()
        self.step_y = 0.0
        self.step_x = 0.0
        self.max_y = 0.0
        self.min_y = 0.0

    def candle_edges(self, candles: list[Candle]):
        init = candles[0]

        self.minc = Candle(init.__dict__)
        self.maxc = Candle(init.__dict__)

        for candle in candles[1:]:
            if candle.open < self.minc.open:
                self.minc.open = candle.open
            if candle.close < self.minc.close:
                self.minc.close = candle.close
            if candle.high < self.minc.high:
                self.minc.high = candle.high
            if candle.low < self.minc.low:
                self.minc.low = candle.low
            if candle.value < self.minc.value:
                self.minc.value = candle.value
            if candle.volume < self.minc.volume:
                self.minc.volume = candle.volume
            if candle.begin < self.minc.begin:
                self.minc.begin = candle.begin
            if candle.end < self.minc.end:
                self.minc.end = candle.end

            if candle.open > self.maxc.open:
                self.maxc.open = candle.open
            if candle.close > self.maxc.close:
                self.maxc.close = candle.close
            if candle.high > self.maxc.high:
                self.maxc.high = candle.high
            if candle.low > self.maxc.low:
                self.maxc.low = candle.low
            if candle.value > self.maxc.value:
                self.maxc.value = candle.value
            if candle.volume > self.maxc.volume:
                self.maxc.volume = candle.volume
            if candle.begin > self.maxc.begin:
                self.maxc.begin = candle.begin
            if candle.end > self.maxc.end:
                self.maxc.end = candle.end

        # x-axe
        self.axe_x = Axe(self.center, self.bottom_right, self.minc, self.maxc)
        # TODO: проверять в каком формате интервалы (минуты, часы, дни)
        self.start = datetime.strptime(str(self.minc.begin), DATETIME_FMT) - timedelta(
            minutes=1
        )
        start = self.start
        self.stop = datetime.strptime(str(self.maxc.begin), DATETIME_FMT) + timedelta(
            minutes=1, seconds=1
        )

        length = float(WIDTH - GAP * 4)
        time_diff = (self.stop - start).total_seconds() / 60
        count_mark = int(time_diff)
        self.step_x = length / count_mark
        x = GAP * 3
        self.axe_x.scales = []

        y_pos = HEIGHT - GAP * 2
        while start < self.stop:
            start += timedelta(minutes=1)
            x += self.step_x
            scale = Scale(
                title=start.strftime("%H:%M"),
                position=Vector2(x, y_pos),
                index=start.minute,
            )
            self.axe_x.scales.append(scale)

        # y-axe
        self.axe_y = Axe(self.up_left, self.center, self.minc, self.maxc)
        self.max_y = float(math.ceil(self.axe_y.max_value))
        self.min_y = float(math.floor(self.axe_y.min_value))

        length = float(HEIGHT - GAP * 3)
        count_mark = int(self.max_y - self.min_y)
        self.step_y = length / count_mark
        self.axe_y.scales = []
        y = HEIGHT - GAP * 2
        i = 0

        while y >= GAP:
            y -= self.step_y
            i += 1
            scale = Scale(
                title=f"{float(self.min_y + i):.2f}",
                position=Vector2(GAP * 3, y),
                index=i,
            )
            self.axe_y.scales.append(scale)

    def set_candles(self, candles: list[Candle]):
        self.candles = candles
        for candle in self.candles:
            mmin = float(min(candle.open, candle.close))
            mmax = float(max(candle.open, candle.close))

            position = Vector2(
                GRAPH.time_to_coord(candle.begin) - GRAPH.step_x / 2.0,
                GRAPH.sum_to_coord(mmax),
            )
            size = Vector2(GRAPH.step_x, GRAPH.step_y * (max(mmax - mmin, GRAPH.thick)))

            candle.position.x, candle.position.y = position.x, position.y
            candle.size.x, candle.size.y = size.x, size.y

    def draw_scale_y(self):
        for scale in self.axe_y.scales:
            left = Vector2(scale.position.x - 5, scale.position.y)
            right = Vector2(scale.position.x + 5, scale.position.y)

            if scale.index % 2 == 0:
                value = f"{float(self.min_y + scale.index):.2f}"
                draw_text(value, GAP - 10, int(scale.position.y - 4), 8, WHITE)

                left = Vector2(scale.position.x - 7.5, scale.position.y)
                right = Vector2(scale.position.x + 7.5, scale.position.y)

            draw_line_ex(left, right, self.thick, BLACK)

    def draw_scale_x(self):  # , min_d: datetime, max_d: datetime):
        # TODO: проверять в каком формате интервалы (минуты, часы, дни)
        for scale in self.axe_x.scales:
            up = Vector2(scale.position.x, scale.position.y - 5.0)
            down = Vector2(scale.position.x, scale.position.y + 5.0)

            if scale.index % 5 == 0:
                up = Vector2(scale.position.x, scale.position.y - 7.5)
                down = Vector2(scale.position.x, scale.position.y + 7.5)
                draw_text(
                    scale.title,
                    int(scale.position.x) - 10,
                    int(scale.position.y) + 10,
                    8,
                    WHITE,
                )

            draw_line_ex(up, down, self.thick, BLACK)

    def draw_axes(self):
        # y-axes
        draw_line_ex(self.axe_y.start_point, self.axe_y.end_point, self.thick, BLACK)

        self.draw_scale_y()

        # x-axes
        draw_line_ex(self.axe_x.start_point, self.axe_x.end_point, self.thick, BLACK)

        self.draw_scale_x()  # min_d=_min, max_d=_max)

    def sum_to_coord(self, value: float) -> float:
        return self.center.y - ((float(value) - self.min_y) * self.step_y)

    def time_to_coord(self, value: datetime) -> float:
        # TODO: проверять интервал (минуты, часы, дни)
        vv = datetime.strptime(str(value), DATETIME_FMT)
        v = (vv - self.start).total_seconds() / 60

        return self.center.x + (v * self.step_x)


GRAPH = Graph(
    up_left=Vector2(GAP * 3, GAP - 10),
    bottom_right=Vector2(WIDTH - GAP, HEIGHT - GAP * 2),
)


def draw_candle(candle: Candle):
    color = GREEN if candle.open <= candle.close else RED
    draw_rectangle_rec(
        (candle.position.x, candle.position.y, candle.size.x, candle.size.y),
        color,
    )
    draw_rectangle_lines_ex(
        (candle.position.x, candle.position.y, candle.size.x, candle.size.y),
        1.0,
        BLACK,
    )

    draw_line_ex(
        Vector2(
            GRAPH.time_to_coord(candle.begin) + 0.5, GRAPH.sum_to_coord(candle.low)
        ),
        Vector2(
            GRAPH.time_to_coord(candle.begin) + 0.5, GRAPH.sum_to_coord(candle.high)
        ),
        1.0,
        color,
    )


def draw_candles(candles: list[Candle]):
    for candle in candles:
        draw_candle(candle)


def run(candles: list[Candle]):
    GRAPH.candle_edges(candles)
    GRAPH.set_candles(candles)

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(FPS)

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)

        GRAPH.draw_axes()
        draw_candles(candles)

        end_drawing()
    close_window()
