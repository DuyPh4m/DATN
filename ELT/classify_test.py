import csv
import requests
import sys

model_name = sys.argv[1]

url = "http://127.0.0.1:5000/api/classify"
user_id = "Sh7sIjpW7DWrciOZchBjp81RwPD2"

with open("./data/raw_dataset.csv", "r") as f:

    reader = csv.DictReader(f)

    for row in reader:
        msg = {"key": user_id, "model_name": model_name, "data": row}
        # print(msg)
        response = requests.post(url, json=msg)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.content)
