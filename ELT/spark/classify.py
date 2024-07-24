from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml import PipelineModel
from pyspark.ml.feature import VectorAssembler
import os
import sys

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0 pyspark-shell"
)


def get_latest_model_path(model_base_path, model_name):
    model_path = os.path.join(model_base_path, model_name)
    model_versions = [
        d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))
    ]
    if not model_versions:
        raise FileNotFoundError(f"No model versions found in {model_path}")
    model_versions.sort()
    latest_model_version = model_versions[-1]
    latest_model_path = os.path.join(model_path, latest_model_version)
    return latest_model_path


spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("Classify")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

model_name = sys.argv[1]
user_id = sys.argv[2]

raw_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "classify")
    .option("failOnDataLoss", "false")
    .load()
)

data_schema = StructType(
    [
        StructField("delta", IntegerType(), True),
        StructField("theta", IntegerType(), True),
        StructField("high_alpha", IntegerType(), True),
        StructField("low_alpha", IntegerType(), True),
        StructField("high_beta", IntegerType(), True),
        StructField("low_beta", IntegerType(), True),
        StructField("low_gamma", IntegerType(), True),
        StructField("middle_gamma", IntegerType(), True),
    ]
)

raw_df = raw_df.selectExpr(
    "CAST(key AS STRING) as key", "CAST(value AS STRING) as value"
)
raw_df = raw_df.withColumn("value", from_json("value", data_schema))

model_base_path = "/app/models/"
model_path = get_latest_model_path(model_base_path, model_name)

# raw_df = raw_df.na.drop()

raw_df = raw_df.select(
    col("value.*"),
    (col("value.delta") / col("value.theta")).alias("delta_theta_ratio"),
    (col("value.delta") / col("value.low_alpha")).alias("delta_low_alpha_ratio"),
    (col("value.delta") / col("value.high_alpha")).alias("delta_high_alpha_ratio"),
    (col("value.delta") / col("value.low_beta")).alias("delta_low_beta_ratio"),
    (col("value.delta") / col("value.high_beta")).alias("delta_high_beta_ratio"),
    (col("value.theta") / col("value.low_alpha")).alias("theta_low_alpha_ratio"),
    (col("value.theta") / col("value.high_alpha")).alias("theta_high_alpha_ratio"),
    (col("value.theta") / col("value.low_beta")).alias("theta_low_beta_ratio"),
    (col("value.theta") / col("value.high_beta")).alias("theta_high_beta_ratio"),
    (
        (col("value.delta") + col("value.theta"))
        / (
            col("value.low_alpha")
            + col("value.high_alpha")
            + col("value.low_beta")
            + col("value.high_beta")
        )
    ).alias("composite_ratio"),
)

feature_cols = [
    "delta",
    "theta",
    "low_alpha",
    "high_alpha",
    "low_beta",
    "high_beta",
    "low_gamma",
    "middle_gamma",
    "delta_theta_ratio",
    "delta_low_alpha_ratio",
    "delta_high_alpha_ratio",
    "delta_low_beta_ratio",
    "delta_high_beta_ratio",
    "theta_low_alpha_ratio",
    "theta_high_alpha_ratio",
    "theta_low_beta_ratio",
    "theta_high_beta_ratio",
    "composite_ratio",
]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
raw_df = assembler.transform(raw_df)

model = PipelineModel.load(model_path)
predictions = model.transform(raw_df)

result_df = predictions.select(
    current_timestamp().alias("timestamp"),
    lit(model_name).alias("model_name"),
    lit(user_id).alias("user_id"),
    predictions["predictedLabel"].alias("predicted_label"),
)

query = (
    result_df.writeStream.outputMode("append")
    .format("org.apache.spark.sql.cassandra")
    .option("spark.cassandra.connection.host", "cassandra")
    .option("spark.cassandra.connection.port", "9042")
    .option("keyspace", "test")
    .option("table", "classify")
    .option("checkpointLocation", "/tmp")
    .start()
)

query.awaitTermination()
