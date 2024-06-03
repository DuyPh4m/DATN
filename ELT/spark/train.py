from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorIndexer, VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
from datetime import datetime
from pyspark.sql.functions import lit
import datetime
import requests

# Create SparkSession
spark = (
    SparkSession.builder.config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("spark://spark-master:7077")
    .appName("Train Model")
    .getOrCreate()
)

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

# Split data into train and test with ratio 80:20
(trainData, testData) = data.randomSplit([0.8, 0.2], seed=1234)

label_col = "classification"
feature_cols = ["attention", "meditation", "delta", "theta", "lowalpha", "highalpha", "lowbeta", "highbeta", "lowgamma", "middlegamma"]

# Create a VectorAssembler
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Index labels, adding metadata to the label column.
labelIndexer = StringIndexer(inputCol=label_col, outputCol="indexedLabel").fit(trainData)

# Automatically identify categorical features, and index them.
featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures", maxCategories=4).fit(trainData)

# Train a RandomForest model.
rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", numTrees=10)

# Convert indexed labels back to original labels.
labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels)

# Chain indexers and forest in a Pipeline
pipeline = Pipeline(stages=[assembler, labelIndexer, featureIndexer, rf, labelConverter])

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
accuracy_df = spark.createDataFrame([(end, type(model).__name__, accuracy, end - start)], ["timestamp", "model", "accuracy", "duration"])

# Write the DataFrame to the accuracy table in Cassandra
accuracy_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .option("spark.cassandra.connection.host", "cassandra") \
    .option("spark.cassandra.connection.port", "9042") \
    .option("keyspace", "test") \
    .option("table", "accuracy") \
    .mode("append") \
    .save()

# Save model
model.save("./models")