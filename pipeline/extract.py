import json

import requests

from db import get_conn

API_URL = 'https://api.open-meteo.com/v1/forecast'
HOURLY = ('temperature_2m,apparent_temperature,relative_humidity_2m,'
          'precipitation,wind_speed_10m,wind_direction_10m,weather_code')


def extract(location: str, latitude: float, longitude: float) -> int:
    """BRONZE: store the API response as-is, return the record id."""
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': HOURLY,
        'past_days': 1,       # yesterday + today: covers missed runs
        'forecast_days': 1,
        'timezone': 'UTC',    # otherwise times arrive in local time with no offset
    }
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO bronze.weather_raw (location, latitude, longitude, raw_data)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (location, latitude, longitude, json.dumps(resp.json())),
        )
        return cur.fetchone()[0]
