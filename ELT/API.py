from flask import Flask, request, jsonify
from confluent_kafka import Producer
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import json
import subprocess
from cassandra.cluster import Cluster

app = Flask(__name__)

parser = ArgumentParser()
parser.add_argument('config_file', type=FileType('r'))
args = parser.parse_args()

# Parse the configuration.
config_parser = ConfigParser()
config_parser.read_file(args.config_file)
config = dict(config_parser['default'])

# Create Producer instance
producer = Producer(config)

def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    data_type = data.get('type')
    user_id = data.get('key')
    value = data.get('value')
    # print(data_type)

    if data_type == 'raw':
        topic = 'raw'
    else:
        topic = 'labeled'
    # print('Received data:', user_id, value)
    producer.produce(topic=topic, value=json.dumps(value), key=user_id, callback=delivery_callback)
    producer.flush()
    return 'Data received', 200

@app.route('/api/train', methods=['POST'])
def train_model():
    spark_bash = "bash spark/train.sh"
    process = subprocess.Popen(spark_bash, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return jsonify({'error': 'Command failed', 'details': stderr.decode('utf-8')}), 500

    cluster = Cluster(['localhost'])
    session = cluster.connect('test')

    query = "SELECT * FROM accuracy ORDER BY timestamp DESC LIMIT 1"

    results = session.execute(query)

    results_dict = {row.key: row.value for row in results}

    return jsonify({"message": "Finshed training model", "result_info": results_dict}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)