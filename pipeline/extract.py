import json
import logging
import time

import requests

from db import get_conn

log = logging.getLogger(__name__)

API_URL = 'https://api.open-meteo.com/v1/forecast'
HOURLY = ('temperature_2m,apparent_temperature,relative_humidity_2m,'
          'precipitation,wind_speed_10m,wind_direction_10m,weather_code')

ATTEMPTS = 4
BASE_DELAY = 2                            # seconds; doubles each retry: 2, 4, 8
RETRY_STATUS = {429, 500, 502, 503, 504}  # transient server-side errors


def fetch(params: dict) -> dict:
    """GET the API, retrying timeouts, connection errors and transient 5xx/429."""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            retryable = (not isinstance(e, requests.HTTPError)
                         or e.response.status_code in RETRY_STATUS)
            if not retryable or attempt == ATTEMPTS:
                raise
            delay = BASE_DELAY * 2 ** (attempt - 1)
            log.warning(f'API request failed ({e.__class__.__name__}), '
                        f'retry {attempt}/{ATTEMPTS - 1} in {delay}s')
            time.sleep(delay)


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
    data = fetch(params)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO bronze.weather_raw (location, latitude, longitude, raw_data)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (location, latitude, longitude, json.dumps(data)),
        )
        return cur.fetchone()[0]
