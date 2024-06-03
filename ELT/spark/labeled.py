from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType
import os

os.environ[
    "PYSPARK_SUBMIT_ARGS"
] = "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0,org.elasticsearch:elasticsearch-spark-20_2.12:8.11.3 pyspark-shell"

spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("Stream Processing")
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

# raw_df = (
#     spark.readStream.format("kafka")
#     .option("kafka.bootstrap.servers", "kafka:9092")
#     .option("subscribe", "raw")
#     .option("failOnDataLoss", "false")
#     .load()
# )

# raw_schema = StructType([
#         StructField("attention", StringType(), True),
#         StructField("meditation", StringType(), True),
#         StructField("delta", StringType(), True),
#         StructField("theta", StringType(), True),
#         StructField("lowalpha", StringType(), True),
#         StructField("highalpha", StringType(), True),
#         StructField("lowbeta", StringType(), True),
#         StructField("highbeta", StringType(), True),
#         StructField("lowgamma", StringType(), True),
#         StructField("highgamma", StringType(), True)
#     ])

labeled_schema = StructType([
        StructField("attention", StringType(), True),
        StructField("meditation", StringType(), True),
        StructField("delta", StringType(), True),
        StructField("theta", StringType(), True),
        StructField("lowalpha", StringType(), True),
        StructField("highalpha", StringType(), True),
        StructField("lowbeta", StringType(), True),
        StructField("highbeta", StringType(), True),
        StructField("lowgamma", StringType(), True),
        StructField("highgamma", StringType(), True),
        StructField("classification", StringType(), True)
    ])

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
    labeled_df["value.attention"].cast("int").alias("attention"),
    labeled_df["value.meditation"].cast("int").alias("meditation"),
    labeled_df["value.delta"].cast("int").alias("delta"),
    labeled_df["value.theta"].cast("int").alias("theta"),
    labeled_df["value.lowalpha"].cast("int").alias("lowalpha"),
    labeled_df["value.highalpha"].cast("int").alias("highalpha"),
    labeled_df["value.lowbeta"].cast("int").alias("lowbeta"),
    labeled_df["value.highbeta"].cast("int").alias("highbeta"),
    labeled_df["value.lowgamma"].cast("int").alias("lowgamma"),
    labeled_df["value.highgamma"].cast("int").alias("highgamma"),
    labeled_df["value.classification"].cast("int").alias("classification")  
)

# processed_labeled_df.writeStream.format("console").start()

# raw_df = raw_df.selectExpr("CAST(key AS STRING) as key", "CAST(value AS STRING) as value")
# # print("raw")
# # raw_df.writeStream.format("console").start()


# raw_df = raw_df.withColumn("value", from_json("value", raw_schema))
# # print("raw")
# # raw_df.writeStream.format("console").start()

# # Perform processing
# processed_raw_df = raw_df.select(
#     current_timestamp().alias("timestamp"),
#     raw_df["value.attention"].cast("int").alias("attention"),
#     raw_df["value.meditation"].cast("int").alias("meditation"),
#     raw_df["value.delta"].cast("int").alias("delta"),
#     raw_df["value.theta"].cast("int").alias("theta"),
#     raw_df["value.lowalpha"].cast("int").alias("lowalpha"),
#     raw_df["value.highalpha"].cast("int").alias("highalpha"),
#     raw_df["value.lowbeta"].cast("int").alias("lowbeta"),
#     raw_df["value.highbeta"].cast("int").alias("highbeta"),
#     raw_df["value.lowgamma"].cast("int").alias("lowgamma"),
#     raw_df["value.highgamma"].cast("int").alias("highgamma")
# )

# processed_raw_df.writeStream.format("console").start()

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

# raw_query = (
#     processed_raw_df.writeStream.outputMode("append")
#     .format("org.apache.spark.sql.cassandra")
#     .option("spark.cassandra.connection.host", "cassandra")
#     .option("spark.cassandra.connection.port", "9042")
#     .option("keyspace", "test")
#     .option("table", "raw")
#     .option("checkpointLocation", "/tmp")
#     .start()
# )

labeled_query.awaitTermination(30)
# raw_query.awaitTermination()
