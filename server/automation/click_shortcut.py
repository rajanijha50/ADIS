import keyboard

KeyShortcuts = {
    'settings':'windows+i',
    'notification_center':'windows+n',
    'quick_panel':'windows+a',
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
    'mute':'volume_mute',
    'home':'home',
    'end':'end',
    'page_up':'page_up',
    'page_down':'page_down',
    'insert':'insert',
    'delete':'delete',
    'escape':'esc',
    'caps_lock':'caps_lock',
    'num_lock':'num_lock',
    'maximize': 'windows+up',
    'minimize': 'windows+down'
}

def handle_click_shortcut(shortcut_name: str) -> bool:
    shortcut_name = shortcut_name.lower().strip()
    if not shortcut_name:
        return "Error: No shortcut name provided."
    if shortcut_name in KeyShortcuts:
        # Keyshortcuts in a dict of predefined shortcuts. where key is the name and value is the actual hotkey combination to trigger
        hotkey = KeyShortcuts[shortcut_name]
        try:
            keyboard.press_and_release(hotkey)
            return True
        except Exception as e:
            print(f"Error executing shortcut '{hotkey}': {e}")
            return False
    return False




