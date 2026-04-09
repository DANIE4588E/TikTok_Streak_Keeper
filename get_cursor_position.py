import pyautogui
import keyboard

pressed = False
while True:
    if keyboard.is_pressed('space') and not pressed: 
        pressed = True
        print(pyautogui.position())
    elif not keyboard.is_pressed('space'):
        pressed = False

 