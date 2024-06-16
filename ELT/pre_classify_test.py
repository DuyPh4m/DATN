import requests
import sys

url = "http://127.0.0.1:5000/api/pre_classify"

user_id = "Sh7sIjpW7DWrciOZchBjp81RwPD2"
model_name = sys.argv[1]

response = requests.post(url, json={"user_id": user_id,"model_name": model_name})

if (
    response.status_code
    == 200
    # and response.headers["Content-Type"] == "application/json"
):
    res = response.json()
    print(res["message"])
else:
    print(f"Unexpected response: {response.content}")
