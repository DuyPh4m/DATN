from pyspark.sql import SparkSession
import shutil
import os
import sys


def get_latest_model_path(model_base_path, user_id, model_name):
    model_path = os.path.join(model_base_path, user_id, model_name)

    model_versions = [
        d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))
    ]

    if not model_versions:
        raise FileNotFoundError(f"No model versions found in {model_path}")

    model_versions.sort()

    latest_model_version = model_versions[-1]
    latest_model_path = os.path.join(model_path, latest_model_version)

    return latest_model_path


if __name__ == "__main__":
    # Create a SparkSession
    spark = SparkSession.builder.appName("Save Model").getOrCreate()

    # Specify the base path and model name
    model_name = sys.argv[1]
    user_id = sys.argv[2]
    model_base_path = "/app/models/tmp/"
    print(model_base_path)

    # Get the latest model path
    latest_model_path = get_latest_model_path(model_base_path, user_id, model_name)

    # Specify the destination path
    destination_path = "/app/models/" + model_name

    # Move the latest model path to the destination
    shutil.move(latest_model_path, destination_path)

    # Stop the SparkSession
    spark.stop()
