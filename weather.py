import aiohttp

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherError(Exception):
    pass


def _wmo_to_condition(code: int) -> str:
    if code in (0, 1):
        return "sunny"
    if code in (2, 3):
        return "cloudy"
    if code in (45, 48):
        return "cloudy"
    if 51 <= code <= 67:
        return "rainy"
    if 71 <= code <= 77:
        return "snowy"
    if 80 <= code <= 82:
        return "rainy"
    if code in (85, 86):
        return "snowy"
    if code in (95, 96, 99):
        return "stormy"
    return "cloudy"


async def geocode(location: str, session: aiohttp.ClientSession) -> tuple[float, float, str]:
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    async with session.get(GEOCODING_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
        if resp.status != 200:
            raise WeatherError(f"Geocoding API returned HTTP {resp.status}.")
        data = await resp.json()

    results = data.get("results")
    if not results:
        raise WeatherError(f"No location found for '{location}'.")

    r = results[0]
    name = r.get("name", location)
    country = r.get("country", "")
    display = f"{name}, {country}".strip(", ")
    return r["latitude"], r["longitude"], display


async def fetch_tomorrow(location: str) -> dict:
    async with aiohttp.ClientSession() as session:
        lat, lon, display = await geocode(location, session)

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
            "forecast_days": 2,
        }
        async with session.get(FORECAST_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status != 200:
                raise WeatherError(f"Forecast API returned HTTP {resp.status}.")
            data = await resp.json()

    daily = data.get("daily", {})
    # index 0 = today, index 1 = tomorrow
    high_c = daily["temperature_2m_max"][1]
    low_c = daily["temperature_2m_min"][1]
    wmo_code = daily["weathercode"][1]

    high_f = round(high_c * 9 / 5 + 32, 1)
    low_f = round(low_c * 9 / 5 + 32, 1)

    return {
        "location": display,
        "high_c": round(high_c, 1),
        "low_c": round(low_c, 1),
        "high_f": high_f,
        "low_f": low_f,
        "condition": _wmo_to_condition(wmo_code),
        "wmo_code": wmo_code,
    }
