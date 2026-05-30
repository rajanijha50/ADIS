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
    # return {
    #     "date":       today.isoformat(),           # 2025-04-16
    #     "day":        today.strftime("%A"),         # Wednesday
    #     "day_short":  today.strftime("%a"),         # Wed
    #     "month":      today.strftime("%B"),         # April
    #     "month_num":  today.month,
    #     "year":       today.year,
    #     "formatted":  today.strftime("%d %B %Y"),  # 16 April 2025
    # }
    return today.strftime("%d %B %Y")


def get_current_ip():
    """Get current IP info """
    data = requests.get("https://ipinfo.io/json").json()
    return data



def get_current_weather():
    """Get current weather using Google Maps API """
    def format_weather(data: dict) -> dict:
        """Format weather API response for text-to-speech output."""
        try:
            return {
                "condition": data["weatherCondition"]["description"]["text"],
                "temperature": f"{data['temperature']['degrees']}°{data['temperature']['unit'][0]}",
                "humidity": f"{data['relativeHumidity']}%",
            }
        except Exception as e:
            return {"error": f"Failed to format weather data: {str(e)}"}
    try:
        IP_data = get_current_ip()
        lat, lon = IP_data["loc"].split(",")
        data = requests.get(f"https://weather.googleapis.com/v1/currentConditions:lookup?key={MAP_API_KEY}&location.latitude={lat}&location.longitude={lon}").json()
        return format_weather(data)
    except Exception as e:
        print("error: ", e)


def handle_get_current(command: str) -> dict | str:
    command = command.lower().strip()
    try:
        if command == 'get_time' or 'time' in command:
            return get_time()
        elif command == 'get_date' or 'date' in command:
            return get_date()
        elif command == 'get_weather' or 'weather' in command:
            return get_current_weather()
        elif command == 'get_ip' or 'ip' in command: 
            ip = get_current_ip()
            return ip['ip']
        else:
            return {'error': f'Invalid command: {command}'}
    
    except Exception as e:
        return {'error': f'Error executing command: {str(e)}'}

    