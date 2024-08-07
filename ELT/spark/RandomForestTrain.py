from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import datetime
import sys


# Create SparkSession
spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("RandomForest Train")
    .getOrCreate()
)

user_id = sys.argv[1]

start = datetime.datetime.now()

# Read records from Cassandra table
data = (
    spark.read.format("org.apache.spark.sql.cassandra")
    .option("spark.cassandra.connection.host", "cassandra")
    .option("spark.cassandra.connection.port", "9042")
    .option("keyspace", "test")
    .option("table", "labeled")
    .option("checkpointLocation", "/tmp")
    .load()
)

data = data.drop("timestamp")

# Check for missing or invalid labels
data = data.na.drop()

data = data.withColumn("delta_theta_ratio", col("delta") / col("theta"))
data = data.withColumn("delta_low_alpha_ratio", col("delta") / col("low_alpha"))
data = data.withColumn("delta_high_alpha_ratio", col("delta") / col("high_alpha"))
data = data.withColumn("delta_low_beta_ratio", col("delta") / col("low_beta"))
data = data.withColumn("delta_high_beta_ratio", col("delta") / col("high_beta"))
data = data.withColumn("theta_low_alpha_ratio", col("theta") / col("low_alpha"))
data = data.withColumn("theta_high_alpha_ratio", col("theta") / col("high_alpha"))
data = data.withColumn("theta_low_beta_ratio", col("theta") / col("low_beta"))
data = data.withColumn("theta_high_beta_ratio", col("theta") / col("high_beta"))
data = data.withColumn(
    "composite_ratio",
    (col("delta") + col("theta"))
    / (col("low_alpha") + col("high_alpha") + col("low_beta") + col("high_beta")),
)

# Split data into train and test with ratio 80:20
label_col = "classification"
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
# Create a VectorAssembler
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
data = assembler.transform(data)

# Index labels, adding metadata to the label column.
labelIndexer = StringIndexer(inputCol=label_col, outputCol="indexedLabel").fit(data)

(trainData, testData) = data.randomSplit([0.8, 0.2], seed=1234)

# Train a RandomForest model.
rf = RandomForestClassifier(
    labelCol="indexedLabel", featuresCol="features", numTrees=20, maxDepth=10
)

# Convert indexed labels back to original labels.
labelConverter = IndexToString(
    inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels
)

# Chain indexers and forest in a Pipeline
pipeline = Pipeline(stages=[labelIndexer, rf, labelConverter])

# Train model. This also runs the indexers.
model = pipeline.fit(trainData)

# Make predictions.
predictions = model.transform(testData)

# Evaluate model
evaluator = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy"
)
accuracy = evaluator.evaluate(predictions)

# Calculate recall
evaluator_recall = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="weightedRecall"
)
weighted_recall = evaluator_recall.evaluate(predictions)

# Calculate F1 score
evaluator_f1 = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="f1"
)
f1_score = evaluator_f1.evaluate(predictions)

end = datetime.datetime.now()

# Create a new DataFrame with the accuracy information
accuracy_df = spark.createDataFrame(
    [
        (
            end,
            user_id,
            type(rf).__name__,
            weighted_recall,
            f1_score,
            accuracy,
            str(end - start),
        )
    ],
    [
        "timestamp",
        "user_id",
        "model_name",
        "weighted_recall",
        "f1_score",
        "accuracy",
        "duration",
    ],
)

# Write the DataFrame to the accuracy table in Cassandra
accuracy_df.write.format("org.apache.spark.sql.cassandra").option(
    "spark.cassandra.connection.host", "cassandra"
).option("spark.cassandra.connection.port", "9042").option("keyspace", "test").option(
    "table", "metrics"
).mode(
    "append"
).save()

save_path = f"/app/models/tmp/{user_id}/RandomForest/{end.strftime('%Y%m%d%H%M%S')}"

# Save model
model.save(save_path)
