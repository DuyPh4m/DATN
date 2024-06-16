import csv
import requests
import sys
from confluent_kafka import Producer
import json

# model_name = sys.argv[1]

config = {"bootstrap.servers": "localhost:9093"}

# Create Producer instance
producer = Producer(config)

url = "http://127.0.0.1:5000/api/classify"
user_id = "Sh7sIjpW7DWrciOZchBjp81RwPD2"

with open("./data/raw_dataset.csv", "r") as f:

    reader = csv.DictReader(f)

    for row in reader:
        # print(msg)
        producer.produce(
            topic="classify",
            value=json.dumps(row)
        )
        producer.flush()
        # response = requests.post(url, json={"user_id": user_id, "data": row})
        # print("Response Status Code:", response.status_code)
        # print("Response Content:", response.content)
