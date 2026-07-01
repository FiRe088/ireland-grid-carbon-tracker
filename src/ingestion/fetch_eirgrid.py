import json
import os
import random
from datetime import datetime

SOURCES = ["wind", "gas", "coal", "interconnector", "hydro", "solar"]

def fetch_and_save():
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(f"/opt/airflow/data/raw/{today}", exist_ok=True)

    records = []
    for source in SOURCES:
        records.append({
            "source_name": source,
            "generation_mw": round(random.uniform(50, 2000), 2),
            "carbon_intensity": round(random.uniform(0, 450), 2),
            "timestamp": today
        })

    output_path = f"/opt/airflow/data/raw/{today}/grid_data.json"
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Saved {len(records)} records to {output_path}")

if __name__ == "__main__":
    fetch_and_save()