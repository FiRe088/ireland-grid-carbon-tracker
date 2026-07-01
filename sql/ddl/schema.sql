CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_source (
    source_id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_generation (
    fact_id SERIAL PRIMARY KEY,
    time_id INT REFERENCES dim_time(time_id),
    source_id INT REFERENCES dim_source(source_id),
    generation_mw NUMERIC,
    carbon_intensity NUMERIC,
    inserted_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (time_id, source_id)
);