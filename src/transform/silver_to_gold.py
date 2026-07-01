import psycopg2
import pandas as pd
import os

def load_to_postgres(run_date: str):
    silver_path = f"/opt/airflow/data/silver/{run_date}"

    if not os.path.exists(silver_path):
        raise FileNotFoundError(f"No silver data at {silver_path}")

    # Read parquet files written by Spark
    df = pd.read_parquet(silver_path)

    conn = psycopg2.connect(
        host="postgres",
        dbname="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()

    for _, row in df.iterrows():
        # Upsert dim_time
        cur.execute("""
            INSERT INTO dim_time (date, year, month, day)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING
            RETURNING time_id
        """, (row['date'], row['year'], row['month'], row['day']))

        result = cur.fetchone()
        if result is None:
            cur.execute("SELECT time_id FROM dim_time WHERE date = %s", (row['date'],))
            result = cur.fetchone()
        time_id = result[0]

        # Upsert dim_source
        cur.execute("""
            INSERT INTO dim_source (source_name)
            VALUES (%s)
            ON CONFLICT (source_name) DO NOTHING
            RETURNING source_id
        """, (row['source_name'],))

        result = cur.fetchone()
        if result is None:
            cur.execute("SELECT source_id FROM dim_source WHERE source_name = %s", (row['source_name'],))
            result = cur.fetchone()
        source_id = result[0]

        # Upsert fact
        cur.execute("""
            INSERT INTO fact_generation (time_id, source_id, generation_mw, carbon_intensity)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (time_id, source_id) DO UPDATE
                SET generation_mw = EXCLUDED.generation_mw,
                    carbon_intensity = EXCLUDED.carbon_intensity
        """, (time_id, source_id, row['generation_mw'], row['carbon_intensity']))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(df)} rows into Postgres gold layer")

if __name__ == "__main__":
    import sys
    load_to_postgres(sys.argv[1])