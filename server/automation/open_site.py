import webbrowser

def handle_open_site(url: str):
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(str(e))
        return False
        
def handle_open_site_by_browser(url: str, browser: str):
    "Open url by specifying browser. default: default browser of the system"
    try:
        webbrowser.open(url, browser)
        return True
    except Exception as e:
        print(str(e))
        return False

