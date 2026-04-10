import ctypes
import cv2
import numpy as np
import pyautogui
import time
from mss import mss
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import pygetwindow as gw
from datetime import datetime

users = ["pushkal.png", "kahlen.png", "encheng.png", "junwei.png", "kalvin.png"]
searchbar_position = (1533, 98)
message_icon_top_left = (1412, 662)
message_icon_bottom_right = (1694, 871)
textbox_position = (1470, 1315)

trigger_now = False

def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def screenshot_region(top_left, bottom_right, output_path="screenshot.png"):
    enable_dpi_awareness()

    left = min(top_left[0], bottom_right[0])
    top = min(top_left[1], bottom_right[1])
    width = abs(bottom_right[0] - top_left[0])
    height = abs(bottom_right[1] - top_left[1])

    if width == 0 or height == 0:
        raise ValueError("Screenshot region must have non-zero width and height.")

    with mss() as sct:
        monitor = {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
        }
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(output_path)

    return output_path


def locate_image_on_virtual_screen(image_path, confidence=0.8):
    enable_dpi_awareness()

    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    with mss() as sct:
        virtual_monitor = sct.monitors[0]
        sct_img = sct.grab(virtual_monitor)

    haystack = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
    haystack_gray = cv2.cvtColor(np.array(haystack), cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(haystack_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_confidence, _, max_loc = cv2.minMaxLoc(result)

    if max_confidence < confidence:
        raise pyautogui.ImageNotFoundException(
            f"Could not locate the image (highest confidence = {max_confidence:.3f})"
        )

    template_height, template_width = template.shape[:2]
    left = virtual_monitor["left"] + max_loc[0]
    top = virtual_monitor["top"] + max_loc[1]
    center_x = left + (template_width // 2)
    center_y = top + (template_height // 2)

    return (center_x, center_y), {
        "left": left,
        "top": top,
        "width": template_width,
        "height": template_height,
        "confidence": max_confidence,
    }



def main():
    triggered = False
    while True:

        now = datetime.now()
        if (now.hour == 0 and now.minute == 0) or trigger_now:
            if not triggered:

                windows = gw.getWindowsWithTitle("Chrome")
                if windows:
                    windows[0].activate()

                pyautogui.hotkey('ctrl', 't')

                time.sleep(0.5)

                pyautogui.click(searchbar_position)

                pyautogui.typewrite("https://www.tiktok.com/messages?lang=en")
                pyautogui.press('enter')

                message_icon_img = cv2.imread("images/message_icon.png")
                message_icon_gray = cv2.cvtColor(message_icon_img, cv2.COLOR_BGR2GRAY)

                while True:
                    time.sleep(0.3)
                    output = screenshot_region(message_icon_top_left, message_icon_bottom_right)
                    output_gray = cv2.cvtColor(cv2.imread(output), cv2.COLOR_BGR2GRAY)
                    similarity = ssim(output_gray, message_icon_gray)
                    if similarity > 0.9:
                        break

                time.sleep(2)
                
                for user in users:
                    image_path = "images\\" + user

                    while True:
                        try:
                            click_point, match = locate_image_on_virtual_screen(image_path, confidence=0.8)
                            break
                        except pyautogui.ImageNotFoundException:
                            time.sleep(0.5)
                    pyautogui.click(click_point[0], click_point[1])
                
                    pyautogui.click(textbox_position)
                    pyautogui.typewrite("Nig")

                    pyautogui.press('enter')

                    time.sleep(0.5)
                
                pyautogui.hotkey('ctrl', 'w')
                triggered = True
        else:
            triggered = False
            
        time.sleep(1)


if __name__ == "__main__":
    main()
