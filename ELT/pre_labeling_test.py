import requests

url = "http://127.0.0.1:5000/api/pre_labeling"

response = requests.post(url)

if (
    response.status_code == 200
    # and response.headers["Content-Type"] == "application/json"
):
    res = response.json()
    print(res["message"])
    print(res["pid"])
else:
    print(f"Unexpected response: {response.content}")

