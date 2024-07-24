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

    subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    return jsonify({"message": "Label job submit successfully"}), 200


@app.route("/api/stop_labeling", methods=["POST"])
def stop_labeling():
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
        jsonify({"message": "Label job stopped successfully"}),
        200,
    )


@app.route("/api/labeling", methods=["POST"])
def receive_labeled_data():
    req = request.get_json()
    value = req.get("value")

    producer.produce(
        topic="labeled",
        value=json.dumps(value),
        callback=delivery_callback
    )

    producer.flush()
    return jsonify({"message": "Labeled data sent successfully"}), 200


@app.route("/api/pre_classify", methods=["POST"])
def pre_classify():
    req = request.get_json()
    user_id = req.get("user_id")
    model_name = req.get("model_name")
    spark_bash = f"bash spark/classify.sh {model_name} {user_id}"

    subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    return (
        jsonify({"message": "Classify job submit successfully"}),
        200,
    )


@app.route("/api/classify", methods=["POST"])
def classify():
    req = request.get_json()
    user_id = req.get("user_id")
    value = req.get("value")

    producer.produce(
        topic="classify",
        value=json.dumps(value),
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
    row = session.execute(statement, (user_id,)).one()

    if row:
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
                        # "user_id": row.user_id,
                        # "timestamp": row.timestamp,
                        "status": current_label,
                    }
                ),
                200,
            )

        # Update previous label
        previous_labels[user_id] = current_label

    return (jsonify({"status": current_label}), 200)


@app.route("/api/stop_classify", methods=["POST"])
def stop_classify():
    spark_bash = "bash spark/stop_classify.sh"

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
        jsonify({"message": "Classify job stopped successfully"}),
        200,
    )


@app.route("/api/train", methods=["POST"])
def train_model():
    req = request.get_json()
    user_id = req.get("user_id")
    model_name = req.get("model_name")

    spark_bash = f"bash spark/{model_name}Train.sh {user_id}"
    
    # if model_name == "RandomForest":
    #     spark_bash = "bash spark/RandomForestTrain.sh " + user_id
    # if model_name == "GBTClassifier":
    #     spark_bash = "bash spark/GBTClassifierTrain.sh " + user_id

    process = subprocess.Popen(
        spark_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return (
            jsonify({"error": "Command failed", "details": stderr.decode("utf-8")}),
            500,
        )

    query = "SELECT * FROM metrics WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"

    result = session.execute(query, (user_id,)).one()

    return (
        jsonify(
            {
                "message": "Finished training model",
                "accuracy": round(result.accuracy, 3),
                "weighted_recall": round(result.weighted_recall, 3),
                "f1_score": round(result.f1_score, 3),
                "duration": result.duration[:10],
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


@app.route("/api/stop_train", methods=["POST"])
def stop_train():
    req = request.get_json()
    model_name = req.get("model_name")

    train_process = model_name + 'Train.py'

    spark_bash = "bash spark/stop_train.sh " + train_process

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
        jsonify({"message": "Train job stopped successfully"}),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
