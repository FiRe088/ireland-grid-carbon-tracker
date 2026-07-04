import json
import os
import random
from datetime import datetime

SOURCES = ["wind", "gas", "coal", "interconnector", "hydro", "solar"]

def fetch_and_save(run_date: str = None):
    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    os.makedirs(f"/opt/airflow/data/raw/{run_date}", exist_ok=True)

    records = []
    for source in SOURCES:
        records.append({
            "source_name": source,
            "generation_mw": round(random.uniform(50, 2000), 2),
            "carbon_intensity": round(random.uniform(0, 450), 2),
            "timestamp": run_date
        })

    output_path = f"/opt/airflow/data/raw/{run_date}/grid_data.json"
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Saved {len(records)} records to {output_path}")

if __name__ == "__main__":
    import sys
    fetch_and_save(sys.argv[1] if len(sys.argv) > 1 else None)