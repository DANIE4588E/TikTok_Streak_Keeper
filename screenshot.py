import ctypes
from ctypes import wintypes

import keyboard
from mss import mss
from PIL import Image


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def get_cursor_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

enable_dpi_awareness()

with mss() as sct:
    while True:
        if keyboard.is_pressed('space'):
            topLeft = get_cursor_pos()
            print("Top Left:", topLeft)
            break

    while keyboard.is_pressed('space'):
        pass

    while True:
        if keyboard.is_pressed('space'):
            bottomRight = get_cursor_pos()
            print("Bottom Right:", bottomRight)
            break

    while keyboard.is_pressed('space'):
        pass

    left = min(topLeft[0], bottomRight[0])
    top = min(topLeft[1], bottomRight[1])
    width = abs(bottomRight[0] - topLeft[0])
    height = abs(bottomRight[1] - topLeft[1])

    monitor = {
        "left": left,
        "top": top,
        "width": width,
        "height": height
    }
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
    img.save("screenshot.png")  