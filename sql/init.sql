CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;

-- BRONZE: сырые данные как пришли из API
CREATE TABLE bronze.weather_raw (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    location    TEXT NOT NULL,
    latitude    FLOAT NOT NULL,
    longitude   FLOAT NOT NULL,
    raw_data    JSONB NOT NULL
);

-- SILVER: очищенные, типизированные записи (одна строка = один час)
CREATE TABLE silver.weather (
    id                  SERIAL PRIMARY KEY,
    bronze_id           INT REFERENCES bronze.weather_raw(id),
    location            TEXT NOT NULL,
    measured_at         TIMESTAMPTZ NOT NULL,
    temperature_c       FLOAT,
    apparent_temp_c     FLOAT,
    humidity_pct        INT,
    precipitation_mm    FLOAT,
    wind_speed_kmh      FLOAT,
    wind_direction_deg  INT,
    weather_code        INT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (location, measured_at)
);

-- GOLD: дневные агрегаты
CREATE TABLE gold.weather_daily (
    id                   SERIAL PRIMARY KEY,
    location             TEXT NOT NULL,
    date                 DATE NOT NULL,
    temp_avg_c           FLOAT,
    temp_min_c           FLOAT,
    temp_max_c           FLOAT,
    precipitation_sum_mm FLOAT,
    wind_speed_avg_kmh   FLOAT,
    wind_speed_max_kmh   FLOAT,
    humidity_avg_pct     FLOAT,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (location, date)
);

-- Индексы для Grafana запросов и алертов
CREATE INDEX ON bronze.weather_raw (fetched_at DESC);
CREATE INDEX ON silver.weather (location, measured_at DESC);
CREATE INDEX ON gold.weather_daily (location, date DESC);
