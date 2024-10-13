import requests

from dotenv import dotenv_values

values = dotenv_values(".env")

def reverse_lookup_location(latitude, longitude):
    r = requests.get(f"http://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={values.get("OPENWEATHER_API_KEY")}").json()

    try:
        return r[0]["name"]
    except:
        return None
