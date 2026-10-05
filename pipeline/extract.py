import json
import os

import requests

from db import get_conn

LOCATION = os.environ['LOCATION']
LATITUDE = os.environ['LATITUDE']
LONGITUDE = os.environ['LONGITUDE']

API_URL = 'https://api.open-meteo.com/v1/forecast'
HOURLY = ('temperature_2m,apparent_temperature,relative_humidity_2m,'
          'precipitation,wind_speed_10m,wind_direction_10m,weather_code')


def extract() -> int:
    """BRONZE: сохраняет ответ API как есть, возвращает id записи."""
    params = {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'hourly': HOURLY,
        'past_days': 1,       # вчера + сегодня: закрывает пропущенные запуски
        'forecast_days': 1,
        'timezone': 'UTC',    # иначе время приходит локальным и без смещения
    }
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO bronze.weather_raw (location, latitude, longitude, raw_data)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (LOCATION, LATITUDE, LONGITUDE, json.dumps(resp.json())),
        )
        return cur.fetchone()[0]
