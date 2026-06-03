from threading import Thread
from automation.open_app import handle_open_app
import keyboard
from asyncio import subprocess
import threading
import time
import winsound
import re
from datetime import datetime, timedelta

# helpers
def _parse_duration(text: str) -> int:
    """
    Parse a natural-language duration into total seconds.
    Handles: '5 minutes', '1 hour 30 minutes', '45 seconds', '2 hours', etc.
    Returns 0 if nothing matched.
    """
    text = text.lower()
    total = 0
    for pattern, multiplier in [
        (r'(\d+)\s*hour', 3600),
        (r'(\d+)\s*min',    60),
        (r'(\d+)\s*sec',     1),
    ]:
        m = re.search(pattern, text)
        if m:
            total += int(m.group(1)) * multiplier

    # print(total)
    return total


def _ring(label: str = "Time's up!"):
    """Beep + print. Replace/extend with a toast notification if you want."""
    print(f"\n🔔 {label}")
    for _ in range(5):
        winsound.Beep(1000, 400)
        time.sleep(0.5)



# main functions
def set_timer(time_duration: str) -> bool:
    """
    Start a countdown timer in a background thread.
    time_duration examples: '5 minutes', '1 hour 30 minutes', '45 seconds'
    """
    try:
        seconds = _parse_duration(time_duration)
        if seconds <= 0:
            print(f"[timer] Couldn't parse duration: '{time_duration}'")
            return False

        def _run():
            print(f"⏱️  Timer started — {time_duration} ({seconds}s)")
            time.sleep(seconds)
            _ring(f"Timer done! ({time_duration})")

        t1 = Thread(target=_run, daemon=False)
        t1.start()
        return True

    except Exception as e:
        print(f"[timer] Error: {e}")
        return False


def set_alarm(alarm_time: str) -> bool:
    """
    Set an alarm for a specific clock time in a background thread.
    alarm_time examples: '7:30 AM', '14:00', '9:05 pm'
    Automatically schedules for tomorrow if the time has already passed today.
    """
    try:
        parsed = None
        for fmt in ('%I:%M %p', '%I:%M%p', '%H:%M'):
            try:
                parsed = datetime.strptime(alarm_time.strip(), fmt)
                break
            except ValueError:
                continue

        if parsed is None:
            print(f"[alarm] Couldn't parse time: '{alarm_time}'")
            return False

        now = datetime.now()
        target = now.replace(hour=parsed.hour, minute=parsed.minute,
                             second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        delay = (target - now).total_seconds()

        def _run():
            print(f"⏰ Alarm set for {alarm_time}  (~{int(delay // 60)} min away)")
            time.sleep(delay)
            _ring(f"ALARM — it's {alarm_time}!")

        threading.Thread(target=_run, daemon=False).start()
        return True

    except Exception as e:
        print(f"[alarm] Error: {e}")
        return False

def write_on_notepad(text: str) -> bool:
    try:
        handle_open_app('notepad')
        time.sleep(0.5)
        keyboard.press_and_release('ctrl+t')
        time.sleep(0.5)
        keyboard.write(text)
        return True
    except Exception as e:
        print(f"Error writing on notepad: {e}")
        return False
        
def handle_control_app(command: str, input_param: str) -> bool:
    command = command.lower().strip()
    if not command:
        return "Error: No command provided."
    try:
        if 'timer' in command:
            return set_timer(input_param)
        elif 'alarm' in command:
            return set_alarm(input_param)
        elif 'notepad' in command:
            return write_on_notepad(input_param)
        else:
            return {'error': f'Invalid control command: {command}'}
    except Exception as e:
        return {'error': f'Error executing control command: {str(e)}'}
        return False

# print(write_on_notepad('hello this is shubham bro'))
# set_timer('30 minutes')
# set_alarm('6:30 pm')
# _ring('shubham')
        
        

