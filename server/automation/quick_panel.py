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
    
def change_brighness(brightness_level = 70):
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


def handle_quick_panel(command: str, level: int = None):
    if command == 'check_os':
        return check_os()
    elif command == "toggle_bluetooth":
        return toggle_bluetooth()
    elif command == "toggle_wifi":
        return toggle_wifi()
    elif command == "check_battery":
        return check_battery()
    elif command == "toggle_notification_center":
        return toggle_notification_center()
    elif command == "change_brighness" and level:
        return change_brighness(level)
    elif command == "change_volume" and level:
        return change_volume(level)
    else:
        return False
    


# print(handle_quick_panel('check_os'))