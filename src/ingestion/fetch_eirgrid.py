import json
import os
import random
import requests
from datetime import datetime

def fetch_and_save(run_date: str = None):
    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    os.makedirs(f"/opt/airflow/data/raw/{run_date}", exist_ok=True)

    url = "https://prodapi.metweb.ie/observations/athenry/today"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        observations = response.json()

        records = []
        for obs in observations:
            wind_speed = obs.get("windSpeed", 0) or 0
            records.append({
                "source_name": "wind",
                "generation_mw": round(float(wind_speed) * 8.5, 2),
                "carbon_intensity": max(0, round(450 - (float(wind_speed) * 12), 2)),
                "timestamp": run_date
            })

        if not records:
            raise ValueError("Empty response from Met Eireann API")

        print(f"Fetched {len(records)} observations from Met Eireann")

    except Exception as e:
        print(f"API call failed: {e} - falling back to synthetic data")
        records = _synthetic_fallback(run_date)

    output_path = f"/opt/airflow/data/raw/{run_date}/grid_data.json"
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Saved {len(records)} records to {output_path}")

def _synthetic_fallback(run_date):
    SOURCES = ["wind", "gas", "coal", "interconnector", "hydro", "solar"]
    return [
        {
            "source_name": s,
            "generation_mw": round(random.uniform(50, 2000), 2),
            "carbon_intensity": round(random.uniform(0, 450), 2),
            "timestamp": run_date
        }
        for s in SOURCES
    ]

if __name__ == "__main__":
    import sys
    fetch_and_save(sys.argv[1] if len(sys.argv) > 1 else None)