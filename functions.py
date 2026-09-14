import json
import cmath
import math
import urllib.parse
import urllib.request


def solve_quadratic(a: float, b: float, c: float):
    """Solve ax^2 + bx + c = 0."""
    if a == 0:
        if b == 0:
            raise ValueError("Not an equation: a and b are both zero.")
        return (-c / b,)

    d = b**2 - 4 * a * c

    if d > 0:
        sqrt_d = math.sqrt(d)
        return ((-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a))
    if d == 0:
        return (-b / (2 * a),)

    sqrt_d = cmath.sqrt(d)
    return ((-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a))

def complex_to_json(obj):
    """JSON encoder fallback: JSON can't serialize complex numbers natively."""
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# WMO weather interpretation codes used by Open-Meteo
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    56: "light freezing drizzle", 57: "dense freezing drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    66: "light freezing rain", 67: "heavy freezing rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow", 77: "snow grains",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    85: "slight snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}

def _get_json(url: str, params: dict):
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=10) as resp:
        return json.load(resp)

def get_weather(city: str):
    """Get current weather for a city using the free Open-Meteo API (no key needed)."""
    geo = _get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": city, "count": 1, "language": "en", "format": "json"},
    )
    if not geo.get("results"):
        return {"error": f"City '{city}' not found."}
    place = geo["results"][0]

    forecast = _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
    )
    current = forecast["current"]
    units = forecast["current_units"]

    return {
        "city": place["name"],
        "country": place.get("country"),
        "time": current["time"],
        "description": WEATHER_CODES.get(current["weather_code"], "unknown"),
        "temperature": f'{current["temperature_2m"]} {units["temperature_2m"]}',
        "feels_like": f'{current["apparent_temperature"]} {units["apparent_temperature"]}',
        "humidity": f'{current["relative_humidity_2m"]} {units["relative_humidity_2m"]}',
        "wind_speed": f'{current["wind_speed_10m"]} {units["wind_speed_10m"]}',
    }
