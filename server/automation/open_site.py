import webbrowser

def handle_open_site(site_name: str):
    try:
        webbrowser.open(site_name)
    except Exception as e:
        print(e)