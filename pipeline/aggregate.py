from db import get_conn


def aggregate():
    """GOLD: пересчитывает дневные агрегаты за последние 3 дня (UTC)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gold.weather_daily
                (location, date, temp_avg_c, temp_min_c, temp_max_c,
                 precipitation_sum_mm, wind_speed_avg_kmh, wind_speed_max_kmh, humidity_avg_pct)
            SELECT
                location,
                measured_at::date AS date,
                ROUND(AVG(temperature_c)::numeric, 1),
                MIN(temperature_c),
                MAX(temperature_c),
                ROUND(SUM(precipitation_mm)::numeric, 2),
                ROUND(AVG(wind_speed_kmh)::numeric, 1),
                MAX(wind_speed_kmh),
                ROUND(AVG(humidity_pct)::numeric, 1)
            FROM silver.weather
            WHERE measured_at >= CURRENT_DATE - 2
            GROUP BY location, measured_at::date
            ON CONFLICT (location, date) DO UPDATE SET
                temp_avg_c           = EXCLUDED.temp_avg_c,
                temp_min_c           = EXCLUDED.temp_min_c,
                temp_max_c           = EXCLUDED.temp_max_c,
                precipitation_sum_mm = EXCLUDED.precipitation_sum_mm,
                wind_speed_avg_kmh   = EXCLUDED.wind_speed_avg_kmh,
                wind_speed_max_kmh   = EXCLUDED.wind_speed_max_kmh,
                humidity_avg_pct     = EXCLUDED.humidity_avg_pct,
                updated_at           = NOW()
        """)
