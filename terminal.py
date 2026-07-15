import logging
import math
from datetime import datetime, timedelta

from pyray import (
    Font,
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    draw_line_dashed,
    draw_line_ex,
    draw_rectangle_lines_ex,
    draw_rectangle_rec,
    draw_text_ex,
    end_drawing,
    get_frame_time,
    get_mouse_position,
    init_window,
    is_key_pressed,
    load_font,
    set_target_fps,
    unload_font,
    window_should_close,
)
from raylib.colors import BLACK, WHITE
from raylib.defines import GLFW_KEY_SPACE, KEY_LEFT, KEY_RIGHT

# from utils import get_candles
from db.repository import get_candles
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
HEIGHT = 900
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

    font: Font

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
            minutes=1,
            seconds=1,
        )

        length = self.center.x + self.bottom_right.x
        time_diff = (self.stop - start).total_seconds() / 60
        count_mark = int(time_diff)
        self.step_x = length / count_mark
        x = self.center.x
        self.axe_x.scales = []
        y = self.center.y

        while x < self.bottom_right.x:
            start += timedelta(minutes=1)
            x += self.step_x
            scale = Scale(
                title=start.strftime("%H:%M"),
                position=Vector2(x, y),
                index=start.minute,
            )
            self.axe_x.scales.append(scale)

        # y-axe
        self.axe_y = Axe(self.up_left, self.center, self.minc, self.maxc)
        self.max_y = float(math.ceil(self.axe_y.max_value))
        self.min_y = float(math.floor(self.axe_y.min_value))

        length = self.center.y - self.up_left.y
        count_mark = int(self.max_y - self.min_y)
        self.step_y = length / count_mark
        self.axe_y.scales = []
        y = self.center.y
        i = 0

        while y > self.up_left.y:
            y -= self.step_y
            i += 1
            scale = Scale(
                title=f"{float(self.min_y + i):.2f}",
                position=Vector2(self.center.x, y),
                index=i,
            )
            self.axe_y.scales.append(scale)

    def set_candles(self, candles: list[Candle]):
        self.candles = candles
        for candle in self.candles:
            mmin = float(min(candle.open, candle.close))
            mmax = float(max(candle.open, candle.close))

            position = Vector2(
                self.time_to_coord(candle.begin) - self.step_x / 2.0,
                self.sum_to_coord(mmax),
            )
            size = Vector2(self.step_x, self.step_y * (max(mmax - mmin, self.thick)))

            candle.position.x, candle.position.y = position.x, position.y
            candle.size.x, candle.size.y = size.x, size.y

    def draw_scale_y(self):
        for scale in self.axe_y.scales:
            left = Vector2(scale.position.x - 5.0, scale.position.y)
            right = Vector2(scale.position.x + 5.0, scale.position.y)

            if scale.index % 2 == 0:
                value = f"{float(self.min_y + scale.index):.2f}"
                draw_text_ex(
                    self.font,
                    value,
                    Vector2(GAP, int(scale.position.y - 8)),
                    16.0,
                    2.0,
                    WHITE,
                )

                left = Vector2(scale.position.x - 7.5, scale.position.y)
                right = Vector2(scale.position.x + 7.5, scale.position.y)

            draw_line_ex(left, right, self.thick, BLACK)

    def draw_scale_x(self):  # , min_d: datetime, max_d: datetime):
        # TODO: проверять в каком формате интервалы (минуты, часы, дни)
        for scale in self.axe_x.scales:
            up = Vector2(scale.position.x, scale.position.y - 5.0)
            down = Vector2(scale.position.x, scale.position.y + 5.0)

            if scale.index % 10 == 0:
                up = Vector2(scale.position.x, scale.position.y - 7.5)
                down = Vector2(scale.position.x, scale.position.y + 7.5)
                draw_text_ex(
                    self.font,
                    scale.title,
                    Vector2(
                        int(scale.position.x) - 22,
                        int(scale.position.y) + 10,
                    ),
                    16.0,
                    2.0,
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

    def coord_to_sum(self, y: float) -> float:
        return self.min_y - ((y - self.center.y) / self.step_y)

    def time_to_coord(self, value: datetime) -> float:
        # TODO: проверять интервал (минуты, часы, дни)
        vv = datetime.strptime(str(value), DATETIME_FMT)
        v = (vv - self.start).total_seconds() / 60

        return self.center.x + (v * self.step_x)


def _draw_candle(graph: Graph, candle: Candle):
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
            graph.time_to_coord(candle.begin) + 0.5, graph.sum_to_coord(candle.low)
        ),
        Vector2(
            graph.time_to_coord(candle.begin) + 0.5, graph.sum_to_coord(candle.high)
        ),
        1.0,
        color,
    )


def _draw_candles(graph: Graph):
    for candle in graph.candles:
        _draw_candle(graph, candle)


def _candle_info(graph: Graph, candle: Candle, position: Vector2):
    color = GREEN if candle.open <= candle.close else RED

    info = {
        "open: ": f"{candle.open} ",
        "close: ": f"{candle.close} ",
        "high: ": f"{candle.high} ",
        "low: ": f"{candle.low} ",
        "percent: ": f"{candle.percent()}%",
    }

    msg: str = ""
    offset_pxl: float = 9.0
    for k, v in info.items():
        draw_text_ex(
            graph.font,
            k,
            Vector2(position.x + len(msg) * offset_pxl, position.y),
            16.0,
            2.0,
            WHITE,
        )
        msg += k
        draw_text_ex(
            graph.font,
            v,
            Vector2(position.x + len(msg) * offset_pxl, position.y),
            16.0,
            2.0,
            color,
        )
        msg += v


def _draw_info(graph: Graph):
    mouse_pos = get_mouse_position()
    position = Vector2(graph.up_left.x + GAP, GAP)
    if not (
        mouse_pos.x >= graph.up_left.x
        and mouse_pos.x <= graph.bottom_right.x
        and mouse_pos.y >= graph.up_left.y
        and mouse_pos.y <= graph.bottom_right.y
    ):
        return

    for candle in graph.candles:
        if not (
            mouse_pos.x >= candle.position.x
            and mouse_pos.x <= candle.position.x + candle.size.x
        ):
            continue

        _candle_info(graph, candle, position)

        # draw dashed pointer
        up = Vector2(candle.position.x + candle.size.x / 2.0, graph.up_left.y)
        down = Vector2(candle.position.x + candle.size.x / 2.0, graph.bottom_right.y)
        left = Vector2(graph.up_left.x, mouse_pos.y)
        right = Vector2(graph.bottom_right.x, mouse_pos.y)
        draw_line_dashed(up, down, 6, 3, WHITE)
        draw_line_dashed(left, right, 6, 3, WHITE)

        # draw candle info
        # TODO: check interval minutes, hours, days
        msg = (
            f"[{candle.begin.strftime('%H:%M')}] {graph.coord_to_sum(mouse_pos.y):.2f}"
        )
        draw_text_ex(
            graph.font,
            msg,
            Vector2(mouse_pos.x + GAP / 2.0, mouse_pos.y - GAP),
            16.0,
            2.0,
            WHITE,
        )


def _draw_timer(graph: Graph, timer: float):
    draw_text_ex(
        graph.font,
        f"{timer:.2f}s",
        Vector2(graph.bottom_right.x - GAP * 5, graph.up_left.y),
        18.0,
        2.0,
        WHITE,
    )


def init(graph: Graph, limit: int = 100, offset: int = 0):
    candles = get_candles(secid="ozon", limit=limit, offset=offset)
    graph.candle_edges(candles)
    graph.set_candles(candles)


def run():
    graph = Graph(
        up_left=Vector2(GAP * 5, GAP * 10),
        bottom_right=Vector2(WIDTH - GAP, HEIGHT - GAP * 4),
    )
    limit = 100
    offset = 0
    init(graph, limit=limit, offset=offset)

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(FPS)

    font = load_font("assets/fonts/SourceCodePro-Medium.ttf")
    graph.font = font

    timer: float = 0.0
    started: bool = False

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)

        graph.draw_axes()
        _draw_candles(graph)

        if is_key_pressed(KEY_RIGHT):
            offset += 1  # limit
            init(graph, limit, offset)
        if is_key_pressed(KEY_LEFT):
            offset -= limit
            init(graph, limit, offset)
        if is_key_pressed(GLFW_KEY_SPACE):
            started = not started
        # TODO: получать данные из БД не каждую секунду
        if started and math.floor(timer) % 1 == 0:
            offset = math.floor(timer)
            init(graph, limit, offset)

        timer += get_frame_time()
        _draw_timer(graph, timer)

        end_drawing()
    unload_font(graph.font)
    close_window()
