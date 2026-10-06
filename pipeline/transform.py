from db import get_conn


def transform(bronze_id: int):
    """SILVER: parse a bronze record into typed hourly rows."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT location, raw_data FROM bronze.weather_raw WHERE id = %s', (bronze_id,))
        location, raw = cur.fetchone()
        h = raw['hourly']
        rows = zip(
            h['time'], h['temperature_2m'], h['apparent_temperature'],
            h['relative_humidity_2m'], h['precipitation'],
            h['wind_speed_10m'], h['wind_direction_10m'], h['weather_code'],
        )
        for time, temp, feels, humidity, precip, wind_spd, wind_dir, code in rows:
            if temp is None:   # hour with no data: skip
                continue
            # DO UPDATE: the forecast for an hour is refined by later runs
            cur.execute(
                """INSERT INTO silver.weather
                   (bronze_id, location, measured_at, temperature_c, apparent_temp_c,
                    humidity_pct, precipitation_mm, wind_speed_kmh, wind_direction_deg, weather_code)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                (bronze_id, location, time + '+00', temp, feels, humidity,
                 precip, wind_spd, wind_dir, code),
            )
