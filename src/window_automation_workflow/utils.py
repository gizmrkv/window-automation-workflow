import re
from typing import Any

import cv2
import numpy as np
import win32gui
from PIL import Image


def is_same_rgb(
    rgb1: tuple[int, ...], rgb2: tuple[int, ...], *, tolerance: int = 0
) -> bool:
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(rgb1, rgb2))


def find_template(
    target: Image.Image,
    template: Image.Image,
    *,
    search_region: tuple[int, int, int, int] | None = None,  # x, y, width, height
) -> tuple[int, int, float]:
    target_width, target_height = target.size

    if search_region is None:
        search_region = (0, 0, target_width, target_height)

    x, y, width, height = search_region

    x_end = min(x + width, target_width)
    y_end = min(y + height, target_height)
    x = max(0, x)
    y = max(0, y)

    target = target.crop((x, y, x_end, y_end))
    target_cv = cv2.cvtColor(np.array(target), cv2.COLOR_RGB2BGR)
    template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(target_cv, template_cv, cv2.TM_CCOEFF_NORMED)

    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    return (max_loc[0] + x, max_loc[1] + y, max_val)


def find_all_templates(
    target: Image.Image,
    template: Image.Image,
    *,
    threshold: float = 0.8,
    search_region: tuple[int, int, int, int] | None = None,  # x, y, width, height
) -> list[tuple[int, int]]:
    target_width, target_height = target.size

    if search_region is None:
        search_region = (0, 0, target_width, target_height)

    x, y, width, height = search_region

    x_end = min(x + width, target_width)
    y_end = min(y + height, target_height)
    x = max(0, x)
    y = max(0, y)

    target_crop = target.crop((x, y, x_end, y_end))
    target_cv = cv2.cvtColor(np.array(target_crop), cv2.COLOR_RGB2BGR)
    template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

    result = cv2.matchTemplate(target_cv, template_cv, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    matches = []
    for pt in zip(*locations[::-1]):
        x_pos = pt[0] + x
        y_pos = pt[1] + y
        matches.append((x_pos, y_pos))

    return matches


def find_windows(title_pattern: str) -> list[tuple[int, str]]:
    windows = []

    def callback(hwnd: int, _: Any):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if re.search(title_pattern, title):
                windows.append((hwnd, title))

    win32gui.EnumWindows(callback, None)
    return windows
