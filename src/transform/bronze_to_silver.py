from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, month, dayofmonth
from pyspark.sql.types import StructType, StructField, StringType, FloatType
import os

def get_spark():
    return SparkSession.builder \
        .appName("IrishGridBronzeToSilver") \
        .master("local[*]") \
        .getOrCreate()

def run_transform(run_date: str):
    spark = get_spark()

    raw_path = f"/opt/airflow/data/raw/{run_date}/grid_data.json"

    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No raw data found at {raw_path}")

    # Define explicit schema — never infer on production pipelines
    schema = StructType([
        StructField("source_name", StringType(), True),
        StructField("generation_mw", DoubleType(), True),
        StructField("carbon_intensity", DOubleType(), True),
        StructField("timestamp", StringType(), True),
    ])

    df = spark.read.schema(schema).json(raw_path)

    # Silver layer: clean, typed, partitioned by date
    silver_df = df \
        .withColumn("date", to_date(col("timestamp"))) \
        .withColumn("year", year(col("date"))) \
        .withColumn("month", month(col("date"))) \
        .withColumn("day", dayofmonth(col("date"))) \
        .filter(col("generation_mw").isNotNull()) \
        .filter(col("carbon_intensity") >= 0)

    silver_path = f"/opt/airflow/data/silver/{run_date}"
    silver_df.write.mode("overwrite").parquet(silver_path)

    print(f"Silver layer written to {silver_path}, row count: {silver_df.count()}")
    spark.stop()

if __name__ == "__main__":
    import sys
    run_transform(sys.argv[1])