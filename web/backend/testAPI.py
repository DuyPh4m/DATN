import csv
import requests
import json
import uuid

url = 'http://127.0.0.1:5000/api/data'

with open('web/dataset/cleanedDataset.csv', 'r') as f:
    
    reader = csv.DictReader(f)

    for row in reader:
        json = {'key': uuid.uuid4().hex, 'value': row}
        # print(json)
        # print(json.get('key'))
        # print(json.get('value'))

        response = requests.post(url, json=json)
        print('Response Status Code:', response.status_code)