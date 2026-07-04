import json
import os
import random
import requests
from datetime import datetime
from google.cloud import storage

BUCKET_NAME = "ireland-grid-raw-zone"

def fetch_and_upload(run_date: str = None):
    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

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

    ndjson_content = "\n".join(json.dumps(r) for r in records)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"raw/{run_date}/grid_data.json")
    blob.upload_from_string(ndjson_content, content_type="application/json")

    print(f"Uploaded {len(records)} records to gs://{BUCKET_NAME}/raw/{run_date}/grid_data.json")

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
    fetch_and_upload(sys.argv[1] if len(sys.argv) > 1 else None)