from config.config import MAP_API_KEY
import datetime
import requests
import subprocess

def get_time() -> dict:
    now = datetime.datetime.now()
    time_24h = now.strftime("%H:%M:%S")
    time_12h = now.strftime("%I:%M %p")
    return time_12h


def get_date() -> dict:
    today = datetime.date.today()
    return today.strftime("%d %B %Y")


def get_current_ip():
    """Get current IP info using Windows shell and local device services."""
    try:
        ip_cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' } | Select-Object -First 1 -ExpandProperty IPAddress)"
        ]
        ip_address = subprocess.check_output(ip_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        if not ip_address:
            raise ValueError("No valid IP address found.")
        
        return ip_address
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve IP or location from Windows shell'}
    except Exception as e:
        return {'error': str(e)}

def get_coordinates():
    """Get geolocation coordinates based on current IP address."""
    try:
        response = requests.get(f"https://ipinfo.io/json").json()
        return response
    except requests.RequestException as e:
        return {"error": f"Failed to retrieve location data: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def get_current_weather():
    """Get current weather using Google Maps API """
    def format_weather(data: dict) -> dict:
        """Format weather API response for text-to-speech output."""
        try:
            return str({
                "condition": data["weatherCondition"]["description"]["text"],
                "temperature": f"{data['temperature']['degrees']}°{data['temperature']['unit'][0]}",
                "humidity": f"{data['relativeHumidity']}%",
            })
        except Exception as e:
            return {"error": f"Failed to format weather data: {str(e)}"}
    try:
        IP_data = get_coordinates()
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
            return get_current_ip()
        elif command == 'get_location' or 'location' in command:
            data = get_coordinates()
            return f"{data.get('city', 'Unknown city')}, {data.get('region', 'Unknown region')}, {data.get('country', 'Unknown country')}"
        else:
            return {'error': f'Invalid command: {command}'}
    
    except Exception as e:
        return {'error': f'Error executing command: {str(e)}'}

    
