from flask import Flask, request, jsonify
from confluent_kafka import Producer
# from argparse import ArgumentParser, FileType
# from configparser import ConfigParser
import json
import subprocess
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

app = Flask(__name__)

# parser = ArgumentParser()
# parser.add_argument("config_file", type=FileType("r"))
# args = parser.parse_args()

# Parse the configuration.
# config_parser = ConfigParser()
# config_parser.read_file(args.config_file)
# config = dict(config_parser["default"])

cluster = Cluster(["localhost"])
session = cluster.connect("test")

config = {
    "bootstrap.servers": "localhost:9093"
}

# Create Producer instance
producer = Producer(config)

# Initialize previous labels as a dictionary to handle multiple users
previous_labels = {}


def delivery_callback(err, msg):
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        if msg.key() is None:
            print(
                "Produced event to topic {topic}: value = {value:12}".format(
                    topic=msg.topic(), value=msg.value().decode("utf-8")
                )
            )
        else:
            print(
                "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(),
                    key=msg.key().decode("utf-8"),
                    value=msg.value().decode("utf-8"),
                )
            )


@app.route("/api/pre_labeling", methods=["POST"])
def pre_labeling():

    spark_bash = "bash spark/labeling.sh"

    process = subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # stdout, stderr = process.communicate()

    # if process.returncode != 0:
    #     # error_message = stderr.decode("utf-8")
    #     # print(f"Error: {error_message}")    
    #     return (
    #         jsonify({"error": "Command failed"}),
    #         500,
    #     )

    return jsonify({"message": "Label job submit successfully", "pid": process.pid}), 200


@app.route("/api/stop_labeling", methods=["POST"])
def stop_labeling():
    # req = request.get_json()
    # pid = req.get("pid")
    spark_bash = "bash spark/stop_labeling.sh"

    process = subprocess.Popen(
            spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return (
            jsonify({"error": "Command failed", "details": stderr.decode("utf-8")}),
            500,
        )    

    return (
        jsonify({"message": "Labeling job stopped successfully"}),
        200,
    )


@app.route("/api/labeling", methods=["POST"])
def receive_labeled_data():
    req = request.get_json()
    # user_id = req.get("key")
    value = req.get("value")

    producer.produce(
        topic="labeled",
        value=json.dumps(value),
        # key=user_id,
        callback=delivery_callback
    )

    producer.flush()
    return "Labeled data sent successfully", 200


@app.route("/api/classify", methods=["POST"])
def receive_raw_data():
    req = request.get_json()
    user_id = req.get("key")
    data = req.get("data")
    model_name = req.get("model_name")

    producer.produce(
        topic="classify",
        value=json.dumps(data),
        key=user_id,
        callback=delivery_callback,
    )
    producer.flush()

    global previous_labels

    # Initialize previous label for the user if not present
    if user_id not in previous_labels:
        previous_labels[user_id] = None

    # Query the latest data point
    query = "SELECT * FROM classify WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"
    statement = SimpleStatement(query)
    rows = session.execute(statement, (user_id,))

    for row in rows:
        current_label = row.predicted_label

        # Check if the label has changed from 0 to 1 or 1 to 0
        if (
            previous_labels[user_id] is not None
            and current_label != previous_labels[user_id]
        ):
            # Update previous label
            previous_labels[user_id] = current_label
            return (
                jsonify(
                    {
                        "user_id": row.user_id,
                        "timestamp": row.timestamp,
                        "status": current_label,
                    }
                ),
                200,
            )

        # Update previous label
        previous_labels[user_id] = current_label

    return (
        jsonify(
            {
                "user_id": row.user_id,
                "timestamp": row.timestamp,
                "status": current_label,
            }
        ),
        200,
    )

@app.route("/api/train", methods=["POST"])
def train_model():
    req = request.get_json()
    user_id = req.get("user_id")
    model = req.get("model")

    if model == "RandomForest":
        spark_bash = "bash spark/RandomForestTrain.sh " + user_id
    if model == "GBTClassifier":
        spark_bash = "bash spark/GBTClassifierTrain.sh " + user_id

    process = subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return (
            jsonify({"error": "Command failed", "details": stderr.decode("utf-8")}),
            500,
        )

    query = "SELECT * FROM accuracy WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"

    result = session.execute(query, (user_id,)).one()

    return (
        jsonify(
            {
                "message": "Finished training model",
                "accuracy": result.accuracy,
                "duration": result.duration,
            }
        ),
        200,
    )

@app.route("/api/save_model", methods=["POST"])
def save_model():
    req = request.get_json()
    user_id = req.get("user_id")
    model_name = req.get("model_name")

    spark_bash = f"bash spark/save_model.sh {model_name} {user_id}"

    process = subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return (
            jsonify({"error": "Command failed", "details": stderr.decode("utf-8")}),
            500,
        )

    return jsonify({"message": "Model saved successfully"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
