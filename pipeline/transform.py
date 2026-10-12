from psycopg2.extras import execute_values

from db import get_conn


def transform(bronze_id: int) -> int:
    """SILVER: parse a bronze record into typed hourly rows, return the row count."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT location, raw_data FROM bronze.weather_raw WHERE id = %s', (bronze_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f'bronze record {bronze_id} not found')
        location, raw = row
        h = raw['hourly']
        hours = zip(
            h['time'], h['temperature_2m'], h['apparent_temperature'],
            h['relative_humidity_2m'], h['precipitation'],
            h['wind_speed_10m'], h['wind_direction_10m'], h['weather_code'],
            strict=True,   # arrays of unequal length mean a malformed response: fail, don't truncate
        )
        rows = [
            (bronze_id, location, ts + '+00', temp, feels, humidity, precip, wind_spd, wind_dir, code)
            for ts, temp, feels, humidity, precip, wind_spd, wind_dir, code in hours
            if temp is not None   # hour with no data: skip
        ]
        # One multi-row statement instead of a round trip per hour.
        # DO UPDATE: the forecast for an hour is refined by later runs
        execute_values(
            cur,
            """INSERT INTO silver.weather
               (bronze_id, location, measured_at, temperature_c, apparent_temp_c,
                humidity_pct, precipitation_mm, wind_speed_kmh, wind_direction_deg, weather_code)
               VALUES %s
               ON CONFLICT (location, measured_at) DO UPDATE SET
                   bronze_id          = EXCLUDED.bronze_id,
                   temperature_c      = EXCLUDED.temperature_c,
                   apparent_temp_c    = EXCLUDED.apparent_temp_c,
                   humidity_pct       = EXCLUDED.humidity_pct,
                   precipitation_mm   = EXCLUDED.precipitation_mm,
                   wind_speed_kmh     = EXCLUDED.wind_speed_kmh,
                   wind_direction_deg = EXCLUDED.wind_direction_deg,
                   weather_code       = EXCLUDED.weather_code,
                   updated_at         = NOW()""",
            rows,
        )
        return len(rows)
