"""
weather_api/weather.py

Fetches current weather for a lat/lon from Open-Meteo and shapes it into
the two model input schemas (solar + wind). Pure library module now --
no CLI/argparse entry point, since this is called from the API layer in
backend/predict_power.py.
"""
import requests

# ---- Target schemas -------------------------------------------------

FEATURE_COLS = [
    "Total solar irradiance (W/m2)",
    "Direct normal irradiance (W/m2)",
    "Global horizontal irradiance (W/m2)",
    "Air temperature (°C)",
    "Atmosphere (hpa)",
    "Relative humidity (%)",
]
TARGET_COL = "Power (MW)"

BASE_FEATURE_COLS = ["wind_speed", "temp", "prs", "hum%"]
POW_TARGET_COL = "pow_out"

# ---- Open-Meteo "current" param names --------------------------------

CURRENT_PARAMS = (
    "shortwave_radiation,direct_normal_irradiance,"
    "global_tilted_irradiance,temperature_2m,"
    "relative_humidity_2m,surface_pressure,wind_speed_10m"
)


def fetch_current(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": CURRENT_PARAMS,
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    current = resp.json()["current"]

    result = {
        # solar model features
        "Total solar irradiance (W/m2)": current["global_tilted_irradiance"],
        "Direct normal irradiance (W/m2)": current["direct_normal_irradiance"],
        "Global horizontal irradiance (W/m2)": current["shortwave_radiation"],
        "Air temperature (°C)": current["temperature_2m"],
        "Atmosphere (hpa)": current["surface_pressure"],
        "Relative humidity (%)": current["relative_humidity_2m"],
        TARGET_COL: None,  # output

        # wind model features
        "wind_speed": current["wind_speed_10m"],
        "temp": current["temperature_2m"],
        "prs": current["surface_pressure"],
        "hum%": current["relative_humidity_2m"],
        POW_TARGET_COL: None,  # output
    }
    return result