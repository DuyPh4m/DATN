from flask import Flask, request
from confluent_kafka import Producer
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import json

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
# producer = Producer(bootstrap_servers='localhost:9092')

def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    user_id = data.get('key')
    value = data.get('value')
    # print('Received data:', user_id, value)
    producer.produce(topic='test', value=json.dumps(value), key=user_id, callback=delivery_callback)
    return 'Data received', 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)