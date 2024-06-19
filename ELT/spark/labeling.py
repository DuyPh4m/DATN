from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType
import os

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0 pyspark-shell"
)

spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("Labeling")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# Define Kafka source
labeled_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "labeled")
    .option("failOnDataLoss", "false")
    .load()
)

# Define schema
labeled_schema = StructType(
    [
        StructField("delta", StringType(), True),
        StructField("theta", StringType(), True),
        StructField("low_alpha", StringType(), True),
        StructField("high_alpha", StringType(), True),
        StructField("low_beta", StringType(), True),
        StructField("high_beta", StringType(), True),
        StructField("classification", StringType(), True)
    ]
)

# Convert binary data to string
labeled_df = labeled_df.selectExpr("CAST(value AS STRING)")
# print("labeled")
# labeled_df.writeStream.format("console").start()

labeled_df = labeled_df.withColumn("value", from_json("value", labeled_schema))
# print("labeled")
# labeled_df.writeStream.format("console").start()


# Perform processing
processed_labeled_df = labeled_df.select(
    current_timestamp().alias("timestamp"),
    labeled_df["value.delta"].cast("float").alias("delta"),
    labeled_df["value.theta"].cast("float").alias("theta"),
    labeled_df["value.low_alpha"].cast("float").alias("low_alpha"),
    labeled_df["value.high_alpha"].cast("float").alias("high_alpha"),
    labeled_df["value.low_beta"].cast("float").alias("low_beta"),
    labeled_df["value.high_beta"].cast("float").alias("high_beta"),
    labeled_df["value.classification"].cast("int").alias("classification")
)

# processed_labeled_df.writeStream.format("console").start()

# Write to Cassandra
labeled_query = (
    processed_labeled_df.writeStream.outputMode("append")
    .format("org.apache.spark.sql.cassandra")
    .option("spark.cassandra.connection.host", "cassandra")
    .option("spark.cassandra.connection.port", "9042")
    .option("keyspace", "test")
    .option("table", "labeled")
    .option("checkpointLocation", "/tmp")
    .start()
)

labeled_query.awaitTermination()