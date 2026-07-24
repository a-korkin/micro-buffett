import logging
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

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
    draw_triangle,
    draw_triangle_lines,
    end_drawing,
    get_frame_time,
    get_mouse_position,
    init_window,
    is_key_pressed,
    is_mouse_button_pressed,
    load_font,
    set_target_fps,
    unload_font,
    window_should_close,
)
from raylib.colors import BLACK, WHITE
from raylib.defines import (
    GLFW_KEY_J,
    GLFW_KEY_K,
    GLFW_KEY_M,
    GLFW_KEY_R,
    GLFW_KEY_SPACE,
    KEY_LEFT,
    KEY_RIGHT,
    MOUSE_LEFT_BUTTON,
)

from algo import make_move, replay_moves
from db import repository
from models.candle import Candle
from models.move import Move, Operation

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
STEP_X = 10.0
RATIO_Y = 9.25


class Mode(Enum):
    OFF = 1
    MOVE_PICKER = 2

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1

        if index >= len(members):
            return members[0]

        return members[index]


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

    interval: repository.Interval

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

    font: Font

    mode: Mode
    balance: float

    def __init__(
        self,
        up_left: Vector2,
        bottom_right: Vector2,
        interval: repository.Interval,
        balance: float,
    ):
        self.up_left = up_left
        self.bottom_right = bottom_right
        self.center = Vector2(up_left.x, bottom_right.y)
        self.interval = interval
        self.start = datetime.today()
        self.stop = datetime.today()
        self.step_y = 0.0
        self.max_y = 0.0
        self.min_y = 0.0
        self.mode = Mode.OFF
        self.balance = balance

    def candle_edges(self):
        init = self.candles[0]

        self.minc = Candle(init.__dict__)
        self.maxc = Candle(init.__dict__)

        for candle in self.candles[1:]:
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
        delta = timedelta(minutes=1)
        if self.interval == repository.Interval.min_15:
            delta = timedelta(minutes=15)
        if self.interval == repository.Interval.hour_1:
            delta = timedelta(hours=1)
        self.start = datetime.strptime(str(self.minc.begin), DATETIME_FMT) - delta
        start = self.start
        self.stop = (
            datetime.strptime(str(self.maxc.begin), DATETIME_FMT)
            + delta
            + timedelta(seconds=1)
        )

        length = self.center.x + self.bottom_right.x
        # time_diff = (self.stop - start).total_seconds() / 60
        # count_mark = int(time_diff)
        x = self.center.x
        self.axe_x.scales = []
        y = self.center.y

        while x < self.axe_x.end_point.x - STEP_X:
            start += delta  # timedelta(minutes=1)
            x += STEP_X
            title = start.strftime("%H:%M")
            scale = Scale(
                title=title,
                position=Vector2(x, y),
                index=start.hour * 100 + start.minute,
            )
            self.axe_x.scales.append(scale)

        # y-axe
        self.axe_y = Axe(self.up_left, self.center, self.minc, self.maxc)
        self.max_y = float(math.ceil(self.axe_y.max_value))
        self.min_y = float(math.floor(self.axe_y.min_value))

        length = self.center.y - self.up_left.y
        count_marks = int(self.max_y - self.min_y)
        self.step_y = length / count_marks
        self.axe_y.scales = []
        y = self.center.y
        i = 0

        step = min(max(math.ceil(RATIO_Y / (self.step_y)), 3), 5)

        while y > self.axe_y.start_point.y:
            y -= self.step_y * step
            i += 1 * step
            scale = Scale(
                title=f"{float(self.min_y + i):.2f}",
                position=Vector2(self.center.x, y),
                index=int(i),
            )
            self.axe_y.scales.append(scale)

    def set_candles(self):
        for candle in self.candles:
            mmin = float(min(candle.open, candle.close))
            mmax = float(max(candle.open, candle.close))

            position = Vector2(
                self.time_to_coord(candle.begin) - STEP_X / 2.0,
                self.sum_to_coord(mmax),
            )
            y = self.step_y * (mmax - mmin)
            size = Vector2(STEP_X, 3.0 if y == 0.0 else y)

            candle.position.x, candle.position.y = position.x, position.y
            candle.size.x, candle.size.y = size.x, size.y

    def draw_scale_y(self):
        for scale in self.axe_y.scales:
            if scale.position.y < self.up_left.y:
                continue

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

    def draw_scale_x(self):
        # TODO: проверять в каком формате интервалы (минуты, часы, дни)
        for scale in self.axe_x.scales:
            up = Vector2(scale.position.x, scale.position.y - 5.0)
            down = Vector2(scale.position.x, scale.position.y + 5.0)

            if (
                (self.interval == repository.Interval.min_1 and scale.index % 10 == 0)
                or (
                    self.interval == repository.Interval.min_15
                    and (scale.index % 100) == 0
                    and (scale.index // 100) % 2 == 0
                )
                or (
                    self.interval == repository.Interval.hour_1
                    and (scale.index % 100) == 0
                    and (scale.index // 100) % 6 == 0
                )
            ):
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
        datetime_val = datetime.strptime(str(value), DATETIME_FMT)
        y_val: float = 0.0
        if self.interval == repository.Interval.min_1:
            y_val = (datetime_val - self.start).total_seconds() / 60
        if self.interval == repository.Interval.min_15:
            y_val = ((datetime_val - self.start).total_seconds() / 60) / 15
        if self.interval == repository.Interval.hour_1:
            y_val = ((datetime_val - self.start).total_seconds() / 60) / 60
        return self.center.x + (y_val * STEP_X)


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


def _candle_info(graph: Graph, candle: Optional[Candle], position: Vector2):
    color = WHITE
    if candle:
        color = GREEN if candle.open <= candle.close else RED

    info = {
        "open: ": f"{candle.open if candle else 0.0} ",
        "close: ": f"{candle.close if candle else 0.0} ",
        "high: ": f"{candle.high if candle else 0.0} ",
        "low: ": f"{candle.low if candle else 0.0} ",
        "percent: ": f"{candle.percent() if candle else 0.0}%",
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


def _get_current_candle(graph: Graph) -> Optional[Candle]:
    mouse_pos = get_mouse_position()
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

        return candle

    return None


def _draw_info(graph: Graph, mouse_position: Vector2, candle: Candle):
    position = Vector2(graph.up_left.x + GAP, GAP)
    _candle_info(graph, candle, position)

    # draw dashed pointer
    if candle:
        up = Vector2(candle.position.x + candle.size.x / 2.0, graph.up_left.y)
        down = Vector2(candle.position.x + candle.size.x / 2.0, graph.bottom_right.y)
        left = Vector2(graph.up_left.x, mouse_position.y)
        right = Vector2(graph.bottom_right.x, mouse_position.y)
        draw_line_dashed(up, down, 6, 3, WHITE)
        draw_line_dashed(left, right, 6, 3, WHITE)

        # draw candle info
        # TODO: check interval minutes, hours, days
        msg = f"[{candle.begin.strftime('%H:%M')}] {graph.coord_to_sum(mouse_position.y):.2f}"
        draw_text_ex(
            graph.font,
            msg,
            Vector2(mouse_position.x + GAP / 2.0, mouse_position.y - GAP),
            16.0,
            2.0,
            WHITE,
        )

    # draw mode
    position.y = GAP * 2
    msg = f"mode: {graph.mode.name}"
    draw_text_ex(graph.font, msg, position, 16.0, 2.0, WHITE)

    # draw balance
    position.y = GAP * 3
    msg = f"balance: {graph.balance:.2f}"
    draw_text_ex(graph.font, msg, position, 16.0, 2.0, WHITE)


def _draw_timer(graph: Graph, timer: float, mils: int):
    draw_text_ex(
        graph.font,
        f"timer: {timer:.2f}s, step mils: {mils}ms",
        Vector2(graph.bottom_right.x - GAP * 16, graph.up_left.y - GAP * 2),
        18.0,
        2.0,
        WHITE,
    )


def _draw_pointer(graph: Graph, candle: Candle, pointer_type: Operation):
    size = 32.0
    x = candle.position.x + STEP_X / 2.0
    y = (
        graph.sum_to_coord(candle.high) - 2.0
        if pointer_type == Operation.SELL
        else graph.sum_to_coord(candle.low) + 2.0
    )

    a = Vector2(x, y)
    b = Vector2(
        x + size,
        y - size * 1.5 if pointer_type == Operation.SELL else y + size * 1.5,
    )
    c = Vector2(
        x - size,
        y - size * 1.5 if pointer_type == Operation.SELL else y + size * 1.5,
    )
    if pointer_type == Operation.SELL:
        draw_triangle(a, b, c, GREEN)
    else:
        draw_triangle(c, b, a, RED)

    draw_triangle_lines(
        a,
        b,
        c,
        GREEN if pointer_type == Operation.SELL else RED,
    )
    draw_text_ex(
        graph.font,
        pointer_type.value.upper(),
        Vector2(
            x - 18.0 if pointer_type == Operation.SELL else x - 13.0,
            y - 40.0 if pointer_type == Operation.SELL else y + 24.0,
        ),
        16.0,
        2.0,
        WHITE,
    )


def init(graph: Graph, candle_slice: list[Candle]):
    graph.candles = candle_slice
    graph.candle_edges()
    graph.set_candles()


def run(secid: str, period: datetime, interval: repository.Interval):
    candles = repository.get_candles(
        secid=secid,
        period=period,
        interval=interval,
        limit=1000,
        offset=0,
    )

    graph = Graph(
        up_left=Vector2(GAP * 5, GAP * 10),
        bottom_right=Vector2(WIDTH - GAP, HEIGHT - GAP * 4),
        interval=interval,
        balance=100_000.0,
    )
    start = 0
    stop = int((graph.bottom_right.x - graph.center.x) / STEP_X)
    total = len(candles)
    init(graph, candles[start:stop])

    init_window(WIDTH, HEIGHT, "Terminal")
    set_target_fps(FPS)

    font = load_font("assets/fonts/SourceCodePro-Medium.ttf")
    graph.font = font

    timer: float = 0.0
    is_started: bool = False
    prev_mils = 0

    # шаг ускорения 20 - каждые 200 миллисекунд, 50 - каждые 500 миллисекунд и т.д.
    accelerations = [50, 20, 10, 5]
    step_indx = 0
    step_mils = accelerations[step_indx]

    # начальные данные для запуска стратегии
    current_candle: Optional[Candle] = None
    last_move: Optional[Move] = None
    moves: list[tuple[Move, Candle]] = []
    sprint_id: UUID = uuid4()

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)

        timer += get_frame_time()

        graph.draw_axes()
        _draw_candles(graph)

        if is_key_pressed(GLFW_KEY_M):
            graph.mode = graph.mode.next()

        if is_key_pressed(GLFW_KEY_R):
            replay_moves(UUID("069fcbc8-c11e-4a84-bc22-4848746616c9"))

        if is_key_pressed(KEY_RIGHT):
            start += 1
            stop += 1
            init(graph, candles[start:stop])

        if is_key_pressed(KEY_LEFT):
            start -= 1
            stop -= 1
            init(graph, candles[start:stop])

        if is_key_pressed(GLFW_KEY_SPACE):
            is_started = not is_started
            if is_started:
                timer = float(start)
                step_indx = 0
                step_mils = accelerations[step_indx]

        if is_started:
            if is_key_pressed(GLFW_KEY_K):
                step_indx += 1
                if step_indx > len(accelerations) - 1:
                    step_indx = 0
                step_mils = accelerations[step_indx]
            if is_key_pressed(GLFW_KEY_J):
                step_indx -= 1
                if step_indx < 0:
                    step_indx = len(accelerations) - 1
                step_mils = accelerations[step_indx]

        milliseconds, _ = math.modf(timer)
        mils = int(milliseconds * 1000)
        current_mils = mils // 10
        if is_started and current_mils % step_mils == 0 and prev_mils != current_mils:
            prev_mils = current_mils
            start += 1
            stop += 1
            if stop <= total:
                init(graph, candles[start:stop])
            else:
                is_started = False

        _draw_timer(graph, timer, step_mils * 10)

        current_candle = _get_current_candle(graph)
        mouse_position = get_mouse_position()
        _draw_info(graph, mouse_position, current_candle)

        if (
            current_candle
            and is_mouse_button_pressed(MOUSE_LEFT_BUTTON)
            and graph.mode == Mode.MOVE_PICKER
        ):
            last_move = make_move(current_candle, last_move, sprint_id, graph.balance)
            moves.append((last_move, current_candle))
            graph.balance = last_move.remain

        # draw moves:
        for move, candle in moves:
            _first_candle = graph.candles[0]
            if _first_candle.begin > candle.begin:
                continue
            _draw_pointer(graph, candle, move.operation)

        end_drawing()
    unload_font(graph.font)
    close_window()
