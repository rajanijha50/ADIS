import keyboard
import time

def handle_open_app(app_name: str):
    app_name = app_name.lower().strip()

    if not app_name:
        return "Error: No application name provided."
    keyboard.press_and_release('win')
    time.sleep(0.5)
    keyboard.write(app_name)
    time.sleep(1)
    keyboard.press_and_release('enter')