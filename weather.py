import aiohttp

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "wizbot-discord/1.0 (github.com/wizardharrytv/discord-wizbot)"}

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

_PLACE_TYPES = {"city", "town", "village", "municipality", "hamlet"}


class WeatherError(Exception):
    pass


def _expand_us_state(location: str) -> str:
    parts = [p.strip() for p in location.split(",")]
    return ", ".join(US_STATES.get(p.upper(), p) for p in parts)


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


def _openmeteo_display(r: dict) -> str:
    name = r.get("name", "")
    country_code = r.get("country_code", "").upper()
    if country_code == "US":
        state = r.get("admin1", "")
        return f"{name}, {state}".strip(", ")
    country = r.get("country", "")
    return f"{name}, {country}".strip(", ")


def _nominatim_score(r: dict) -> int:
    if r.get("class") == "place" and r.get("type") in _PLACE_TYPES:
        return 2
    if r.get("class") == "boundary" and r.get("type") == "administrative":
        return 1
    return 0


def _nominatim_display(r: dict) -> str:
    addr = r.get("address", {})
    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or addr.get("suburb")
        or addr.get("county")
        or ""
    )
    country_code = addr.get("country_code", "").upper()
    if country_code == "US":
        state = addr.get("state", "")
        return f"{city}, {state}".strip(", ") or addr.get("country", "Unknown")
    country = addr.get("country", "")
    return f"{city}, {country}".strip(", ") or addr.get("country", "Unknown")


async def geocode(location: str, session: aiohttp.ClientSession) -> tuple[float, float, str]:
    query = _expand_us_state(location)

    # Primary: Open-Meteo geocoding
    params = {"name": query, "count": 1, "language": "en", "format": "json"}
    async with session.get(GEOCODING_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
        if resp.status == 200:
            data = await resp.json()
            results = data.get("results")
            if results:
                r = results[0]
                return r["latitude"], r["longitude"], _openmeteo_display(r)

    # Fallback: Nominatim (OpenStreetMap)
    params = {"q": query, "limit": 3, "format": "json", "addressdetails": 1}
    async with session.get(
        NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS, timeout=aiohttp.ClientTimeout(total=8)
    ) as resp:
        if resp.status != 200:
            raise WeatherError(f"Geocoding failed (HTTP {resp.status}).")
        results = await resp.json()

    if not results:
        raise WeatherError(f"No location found for '{location}'.")

    best = max(results, key=_nominatim_score)
    return float(best["lat"]), float(best["lon"]), _nominatim_display(best)


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
