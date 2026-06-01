from automation.click_shortcut import handle_click_shortcut
import subprocess
import others.toggle_bluetooth as bt
import others.toggle_wifi as wifi
import platform


def check_os():
    os_type = platform.system()
    return os_type
def toggle_bluetooth():
    subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', bt.bluetooth_path],
        capture_output=True,
        text=True
    )

    return True
def toggle_wifi():
    subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', wifi.wifi_path],
        capture_output=True,
        text=True
    )

    return True
def check_battery():
    result = subprocess.run(
        ['powershell', '-command', '(Get-WmiObject Win32_Battery).EstimatedChargeRemaining'],
        capture_output=True,
        text=True
    )

    return result.stdout.strip() + '%'
def toggle_notification_center():
    handle_click_shortcut('windows+n')
    return True
    
def change_brightness(brightness_level=70):
    """Set system brightness (0-100)."""
    brightness_level = int(brightness_level.replace('%', '')) if isinstance(brightness_level, str) else brightness_level
    brightness_level = max(0, min(100, brightness_level))
    try:
        result = subprocess.run(
            ['powershell', '-command', f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{brightness_level})'],
            capture_output=True,
            text=True
        )
        return True
    except Exception:
        return False
def change_volume(volume_level=50):
    """
    Changes the system volume (0-100) using PowerShell and the .NET Core Audio API.
    """
    volume_level = int(volume_level.replace('%', '')) if isinstance(volume_level, str) else volume_level
    volume_level = max(0, min(100, volume_level))
    
    # scalar_volume = volume_level / 100.0
    
    direct_ps_command = f"(Get-WmiObject -Query 'Select * from Win32_DesktopMonitor'); " \
                        f"$w = New-Object -ComObject WScript.Shell; " \
                        f"1..50 | % {{ $w.SendKeys([char]174) }}; " \
                        f"1..{volume_level // 2} | % {{ $w.SendKeys([char]175) }}"

    try:
        result = subprocess.run(
            ['powershell', '-Command', direct_ps_command],
            capture_output=True,
            text=True
        )
        return True
    except Exception:
        return False


def handle_quick_panel(command: str, level: int = None) -> bool | str:
    command = command.lower().strip()
    if command=='check_os' or 'check_os' in command:
        return check_os()
    elif command=='toggle_bluetooth' or 'toggle_bluetooth' in command:
        return toggle_bluetooth()
    elif command=='toggle_wifi' or 'toggle_wifi' in command:
        return toggle_wifi()
    elif command=='check_battery' or 'check_battery' in command:
        return check_battery()
    elif command=='toggle_notification_center' or 'toggle_notification_center' in command:
        return toggle_notification_center()
    elif command=='change_brightness' or 'change_brightness' in command and level is not None:
        return change_brightness(level)
    elif command=='change_volume' or 'change_volume' in command and level is not None:
        return change_volume(level)
    else:
        print(f"Unknown quick panel command: '{command}'")
        return False
    


# print(handle_quick_panel('check_os'))