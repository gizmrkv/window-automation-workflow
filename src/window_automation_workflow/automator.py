import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pyautogui
import win32con
import win32gui
from PIL import Image

from .utils import (
    find_all_templates,
    find_template,
    find_windows,
)


class Automator:
    def __init__(
        self, title_pattern: str, *, screenshot_dir: str | Path = "screenshot"
    ):
        self.title_pattern = title_pattern
        self.screenshot_dir = Path(screenshot_dir)

        windows = find_windows(title_pattern)

        if len(windows) == 0:
            raise RuntimeError(f"Window not found: {title_pattern}")

        if len(windows) > 1:
            raise RuntimeError(f"Multiple windows found: {title_pattern}")

        self.hwnd, self.title = windows[0]

    def wait_until(
        self,
        predicate: Callable[[], bool],
        *,
        timeout: float | None = None,
        interval: float = 0.1,
    ):
        start_time = time.time()
        while True:
            if timeout is not None and time.time() - start_time > timeout:
                break

            start_step_time = time.time()
            if predicate():
                break

            elapsed_time = time.time() - start_step_time
            if elapsed_time < interval:
                time.sleep(interval - elapsed_time)

    def wait_while(
        self,
        predicate: Callable[[], bool],
        *,
        timeout: float | None = None,
        interval: float = 0.1,
    ):
        start_time = time.time()
        while True:
            if timeout is not None and time.time() - start_time > timeout:
                break

            start_step_time = time.time()
            if not predicate():
                break

            elapsed_time = time.time() - start_step_time
            if elapsed_time < interval:
                time.sleep(interval - elapsed_time)

    def move_to(
        self, x: int | float, y: int | float, **move_to_kwargs: Any
    ) -> tuple[int, int]:
        x, y = self.window_to_screen(x, y)
        pyautogui.moveTo(x, y, **move_to_kwargs)
        return x, y

    def move_to_template(
        self,
        template: Image.Image,
        *,
        search_region: tuple[int, int, int, int] | None = None,
        threshold: float = 0.8,
        **move_to_kwargs: Any,
    ) -> tuple[int, int] | None:
        if xy := self.find_template(
            template, search_region=search_region, threshold=threshold
        ):
            template_w, template_h = template.size
            x, y = xy
            x += template_w // 2
            y += template_h // 2
            self.move_to(x, y, **move_to_kwargs)
            return x, y

    def click(
        self, x: int | float, y: int | float, *, delay: float = 0.0, **click_kwargs: Any
    ) -> tuple[int, int]:
        x, y = self.window_to_screen(x, y)
        if delay > 0:
            pyautogui.moveTo(x, y)
            time.sleep(delay)

        pyautogui.click(x, y, **click_kwargs)
        return x, y

    def click_template(
        self,
        template: Image.Image,
        *,
        search_region: tuple[int, int, int, int] | None = None,
        threshold: float = 0.8,
        delay: float = 0.0,
        **click_kwargs: Any,
    ) -> tuple[int, int] | None:
        if xy := self.find_template(
            template, search_region=search_region, threshold=threshold
        ):
            template_w, template_h = template.size
            x, y = xy
            x, y = self.window_to_screen(x, y)
            x += template_w // 2
            y += template_h // 2
            if delay > 0:
                pyautogui.moveTo(x, y)
                time.sleep(delay)
            pyautogui.click(x, y, **click_kwargs)
            return x, y

    def drag_to(
        self, x: int | float, y: int | float, **drag_to_kwargs: Any
    ) -> tuple[int, int]:
        x, y = self.window_to_screen(x, y)
        pyautogui.dragTo(x, y, **drag_to_kwargs)
        return x, y

    def activate(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def move_window(self, x: int, y: int):
        _, _, width, height = win32gui.GetWindowRect(self.hwnd)
        win32gui.MoveWindow(self.hwnd, x, y, width, height, True)

    def resize(self, width: int, height: int):
        x, y, _, _ = win32gui.GetWindowRect(self.hwnd)
        win32gui.MoveWindow(self.hwnd, x, y, width, height, True)

    def screenshot(self, save_dir: str | Path | None = None) -> Image.Image:
        rect = win32gui.GetWindowRect(self.hwnd)
        x, y, right, bottom = rect
        width = right - x
        height = bottom - y

        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        if save_dir:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            filepath = save_path / f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            screenshot.save(filepath)

        return screenshot

    def window_to_screen(self, x: int | float, y: int | float) -> tuple[int, int]:
        window_rect = win32gui.GetWindowRect(self.hwnd)
        window_x, window_y, window_w, window_h = window_rect

        if isinstance(x, float):
            x = int(window_x + window_w * x)
        if isinstance(y, float):
            y = int(window_y + window_h * y)

        x += window_x
        y += window_y

        return x, y

    def find_template(
        self,
        template: Image.Image,
        *,
        threshold: float = 0.8,
        search_region: tuple[int, int, int, int] | None = None,
    ) -> tuple[int, int] | None:
        screenshot = self.screenshot()
        x, y, score = find_template(screenshot, template, search_region=search_region)
        if score >= threshold:
            return x, y

    def find_all_templates(
        self,
        template: Image.Image,
        *,
        threshold: float = 0.8,
        search_region: tuple[int, int, int, int] | None = None,
    ) -> list[tuple[int, int]]:
        screenshot = self.screenshot()
        matches = find_all_templates(
            screenshot, template, threshold=threshold, search_region=search_region
        )
        return matches

    def pixel(self, x: int | float, y: int | float) -> tuple[int, int, int]:
        x, y = self.window_to_screen(x, y)
        pixel_color = pyautogui.pixel(x, y)
        return pixel_color
