from config.config import MAP_API_KEY
import datetime
import requests

def get_time() -> dict:
    now = datetime.datetime.now()
    return {
        "time_24h": now.strftime("%H:%M:%S"),
        "time_12h": now.strftime("%I:%M:%S %p"),
        "hour":     now.hour,
        "minute":   now.minute,
        "second":   now.second,
    }


def get_date() -> dict:
    today = datetime.date.today()
    return {
        "date":       today.isoformat(),           # 2025-04-16
        "day":        today.strftime("%A"),         # Wednesday
        "day_short":  today.strftime("%a"),         # Wed
        "month":      today.strftime("%B"),         # April
        "month_num":  today.month,
        "year":       today.year,
        "formatted":  today.strftime("%d %B %Y"),  # 16 April 2025
    }


def get_current_ip():
    """Get current IP info """
    data = requests.get("https://ipinfo.io/json").json()
    return data

def get_current_weather():
    """Get current weather using Google Maps API """
    
    try:
        IP_data = get_current_ip()
        lat, lon = IP_data["loc"].split(",")
        data = requests.get(f"https://weather.googleapis.com/v1/currentConditions:lookup?key={MAP_API_KEY}&location.latitude={lat}&location.longitude={lon}").json()
        return data
    except Exception as e:
        print("error: ", e)


def handle_get_current(command: str):
    command = command.lower()
    if "time" in command:
        return get_time()
    elif "date" in command:
        return get_date()
    elif "weather" in command:
        return get_current_weather()
    else:
        return 'Invalid command'
    
