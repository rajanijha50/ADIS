import keyboard
import time

def handle_open_app(appName: str) -> bool:
    try:
        keyboard.press_and_release('win')
        time.sleep(1)
        keyboard.write(appName.lower())
        time.sleep(1.5)
        keyboard.press_and_release('enter')
        return True
    except Exception as e:
        print(f"Error opening {appName}: {e}")
        return False

# print(handle_open_app('clock'))