import requests
import json
import sys

url = "http://127.0.0.1:5000/api/stop_labeling"

headers = {"Content-Type": "application/json"}

# Replace this with the actual data you want to send
# data = {"pid": sys.argv[1]}

response = requests.post(url, headers=headers, data=json.dumps({}))

if response.status_code == 200:
    res = response.json()
    print(res["message"])
else:
    print(f"Unexpected response: {response.content}")
