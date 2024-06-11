import csv
import requests
# import uuid

url = 'http://127.0.0.1:5000/api/labeling'

with open('./data/labeled_dataset.csv', 'r') as f:
    
    reader = csv.DictReader(f)

    for row in reader:
        msg = {'type': 'labeled', 'value': row}
        # print(json)
        # print(json.get('key'))
        # print(json.get('value'))

        response = requests.post(url, json=msg)
        print('Response Status Code:', response.status_code)

