import webbrowser

def handle_open_site(site_name: str):
    site_name = site_name.lower().strip()
    if not site_name:
        return "Error: No site name provided."
    try:
        webbrowser.open(site_name)
    except Exception as e:
        print(e)