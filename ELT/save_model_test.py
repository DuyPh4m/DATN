import requests
import sys

url = "http://127.0.0.1:5000/api/save_model"

user_id = "Sh7sIjpW7DWrciOZchBjp81RwPD2"
model_name = sys.argv[1]

response = requests.post(url, json={"user_id": user_id, "model_name": model_name})

if response.text:
    res = response.json()
    print("Response Status Code:", response.status_code)
    if response.status_code == 500:
        print("Error:", res["error"])
    else:
        print("Message:", res["message"])
else:
    print("Empty response")
