from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
import datetime
import sys

# Create SparkSession
spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("Train Model")
    .getOrCreate()
)

user_id = sys.argv[1]

# Read records from Cassandra table
data = (
    spark.read
    .format("org.apache.spark.sql.cassandra")
    .option("spark.cassandra.connection.host", "cassandra")
    .option("spark.cassandra.connection.port", "9042")
    .option("keyspace", "test")
    .option("table", "labeled")
    .option("checkpointLocation", "/tmp")
    .load()
)

data = data.drop("timestamp")

# Check for missing or invalid labels
data = data.na.drop(subset=["classification"])

# Convert label column to integer type if necessary
data = data.withColumn("classification", data["classification"].cast("int"))

# Split data into train and test with ratio 80:20
label_col = "classification"
feature_cols = ["attention", "meditation", "delta", "theta", "lowalpha", "highalpha", "lowbeta", "highbeta", "lowgamma", "middlegamma"]

# Create a VectorAssembler
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
data = assembler.transform(data)

# Index labels, adding metadata to the label column.
labelIndexer = StringIndexer(inputCol=label_col, outputCol="indexedLabel").fit(data)

(trainData, testData) = data.randomSplit([0.8, 0.2], seed=1234)

# Train a RandomForest model.
rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="features", numTrees=10)

# Convert indexed labels back to original labels.
labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels)

# Chain indexers and forest in a Pipeline
pipeline = Pipeline(stages=[labelIndexer, rf, labelConverter])

start = datetime.datetime.now()
# Train model. This also runs the indexers.
model = pipeline.fit(trainData)

# Make predictions.
predictions = model.transform(testData)

# Evaluate model
evaluator = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)

end = datetime.datetime.now()

# Create a new DataFrame with the accuracy information
accuracy_df = spark.createDataFrame([(end, user_id, type(rf).__name__, accuracy, str(end - start))], ["timestamp", "user_id", "model", "accuracy", "duration"])

# Write the DataFrame to the accuracy table in Cassandra
accuracy_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .option("spark.cassandra.connection.host", "cassandra") \
    .option("spark.cassandra.connection.port", "9042") \
    .option("keyspace", "test") \
    .option("table", "accuracy") \
    .mode("append") \
    .save()

save_path = f"./models/{end}_{user_id}"

# Save model
model.save(save_path)
