from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, from_json, lit
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.ml import PipelineModel
from pyspark.ml.feature import VectorAssembler
import os
import sys

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0,org.elasticsearch:elasticsearch-spark-20_2.12:8.11.3 pyspark-shell"
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

# Define Kafka source
raw_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "classify")
    .option("failOnDataLoss", "false")
    .load()
)

data_schema = StructType(
    [
        StructField("delta", StringType(), True),
        StructField("theta", StringType(), True),
        StructField("low_alpha", StringType(), True),
        StructField("high_alpha", StringType(), True),
        StructField("low_beta", StringType(), True),
        StructField("high_beta", StringType(), True),
    ]
)

raw_df = raw_df.selectExpr(
    "CAST(key AS STRING) as key", "CAST(value AS STRING) as value"
)
# print("raw")
# raw_df.writeStream.format("console").start()


raw_df = raw_df.withColumn("value", from_json("value", data_schema))

model_base_path = "/app/models/"

model_path = get_latest_model_path(model_base_path, model_name)
# print("raw")
# raw_df.writeStream.format("console").start()

feature_cols = [
    "delta",
    "theta",
    "low_alpha",
    "high_alpha",
    "low_beta",
    "high_beta",
]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

raw_df = raw_df.select(
    raw_df["value.delta"].cast("float").alias("delta"),
    raw_df["value.theta"].cast("float").alias("theta"),
    raw_df["value.low_alpha"].cast("float").alias("low_alpha"),
    raw_df["value.high_alpha"].cast("float").alias("high_alpha"),
    raw_df["value.low_beta"].cast("float").alias("low_beta"),
    raw_df["value.high_beta"].cast("float").alias("high_beta"),
)
raw_df = raw_df.na.drop()

processed_df = assembler.transform(raw_df)

model = PipelineModel.load(model_path)

predictions = model.transform(processed_df)

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
