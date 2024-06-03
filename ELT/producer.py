import uuid
from confluent_kafka import Producer
import csv

# brokers = ["kafka1:9093", "kafka2:9095", "kafka3:9097"]

brokers = ["localhost:9093"]

producer_conf = {"bootstrap.servers": ",".join(brokers)}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
  
def send_message(producer, topic, csv_path):
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            key = str(uuid.uuid4())  # Get and remove the first field as the key
            value = ','.join(row.values())  # Join the remaining fields as the value

            # Send the record to Kafka
            producer.produce(topic, key=key, value=value, callback=delivery_report)
            producer.flush()        
    print('Finished sending all messages!')    

if __name__ == '__main__':
    try:
        send_message(producer, 'EPL', './data/results.csv')
    except Exception as e:
        print(e)