import json
import random
from datetime import datetime
from google.cloud import storage

SOURCES = ["wind", "gas", "coal", "interconnector", "hydro", "solar"]
BUCKET_NAME = "ireland-grid-raw-zone"

def fetch_and_upload(run_date: str = None):
    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    records = []
    for source in SOURCES:
        records.append({
            "source_name": source,
            "generation_mw": round(random.uniform(50, 2000), 2),
            "carbon_intensity": round(random.uniform(0, 450), 2),
            "timestamp": run_date
        })

    ndjson_content = "\n".join(json.dumps(r) for r in records)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"raw/{run_date}/grid_data.json")
    blob.upload_from_string(ndjson_content, content_type="application/json")

    print(f"Uploaded {len(records)} records to gs://{BUCKET_NAME}/raw/{run_date}/grid_data.json")

if __name__ == "__main__":
    import sys
    fetch_and_upload(sys.argv[1] if len(sys.argv) > 1 else None)