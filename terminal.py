from pyray import (
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    draw_rectangle_v,
    end_drawing,
    init_window,
    set_target_fps,
    window_should_close,
)

BACKGROUND_COLOR = (39, 51, 56, 255)
RED = (224, 84, 84, 255)
GREEN = (43, 87, 72, 255)


def run():
    init_window(800, 600, "Terminal")
    set_target_fps(60)

    pos = Vector2(200.0, 100.0)
    size = Vector2(30.0, 50.0)

    while not window_should_close():
        begin_drawing()
        clear_background(BACKGROUND_COLOR)
        draw_rectangle_v(pos, size, GREEN)
        end_drawing()
    close_window()
