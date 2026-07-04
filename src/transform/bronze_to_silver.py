from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, month, dayofmonth
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import os

def get_spark():
    return SparkSession.builder \
        .appName("IrishGridBronzeToSilver") \
        .master("local[*]") \
        .config("spark.jars", "/opt/airflow/gcs-connector.jar") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/airflow/gcp-key.json") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .getOrCreate()

def run_transform(run_date: str, destination: str = "local"):
    spark = get_spark()

    if destination == "gcs":
        raw_path = f"gs://ireland-grid-raw-zone/raw/{run_date}/grid_data.json"
        silver_path = f"gs://ireland-grid-raw-zone/silver/{run_date}"
    else:
        raw_path = f"/opt/airflow/data/raw/{run_date}/grid_data.json"
        silver_path = f"/opt/airflow/data/silver/{run_date}"

    if destination == "local" and not os.path.exists(raw_path):
        raise FileNotFoundError(f"No raw data found at {raw_path}")

    schema = StructType([
        StructField("source_name", StringType(), True),
        StructField("generation_mw", DoubleType(), True),
        StructField("carbon_intensity", DoubleType(), True),
        StructField("timestamp", StringType(), True),
    ])

    df = spark.read.schema(schema).json(raw_path)

    silver_df = df \
        .withColumn("date", to_date(col("timestamp"))) \
        .withColumn("year", year(col("date"))) \
        .withColumn("month", month(col("date"))) \
        .withColumn("day", dayofmonth(col("date"))) \
        .filter(col("generation_mw").isNotNull()) \
        .filter(col("carbon_intensity") >= 0)

    silver_df.write.mode("overwrite").parquet(silver_path)
    print(f"Silver layer written to {silver_path}, row count: {silver_df.count()}")
    spark.stop()

if __name__ == "__main__":
    import sys
    run_transform(sys.argv[1])