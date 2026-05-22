import keyboard

KeyShortcuts = {
    'settings':'windows+i',
    'notification_center':'windows+n',
    'reload':'ctrl+r',
    'switch':'alt+tab',
    'search':'alt+space',
    'file_explorer':'windows+e',
    'desktop':'windows+d',
    'run':'windows+r',
    'lock':'windows+l',
    'task_manager':'ctrl+shift+esc',
    'screenshot':'windows+shift+s',
    'screen_recording':'windows+alt+r',
    'copy':'ctrl+c',
    'paste':'ctrl+v',
    'cut':'ctrl+x',
    'undo':'ctrl+z',
    'redo':'ctrl+y',
    'select_all':'ctrl+a',
    'new_tab':'ctrl+t',
    'close_tab':'ctrl+w',
    'refresh':'f5',
    'print_screen':'print_screen',
    'volume_up':'volume up',
    'volume_down':'volume down',
    'mute':'volume mute',
    'play/pause':'play/pause media',
    'next_track':'next track',
    'previous_track':'previous track',
    'increase_brightness':'brightness up',
    'decrease_brightness':'brightness down',
    'home':'home',
    'end':'end',
    'page_up':'page up',
    'page_down':'page down',
    'insert':'insert',
    'delete':'delete',
    'escape':'esc',
    'caps_lock':'caps lock',
    'num_lock':'num lock',
    'maximize': 'windows + up',
    'minimize': 'windows + down'
}

def handle_click_shortcut(shortcut: str) -> bool:
    if shortcut in KeyShortcuts:
        hotkey = KeyShortcuts[shortcut]
        try:
            keyboard.press_and_release(hotkey)
            return True
        except Exception as e:
            print(f"Error executing shortcut '{hotkey}': {e}")
            return False
            
    print(f"Shortcut '{shortcut}' not found in KeyShortcuts dictionary.")
    return False

