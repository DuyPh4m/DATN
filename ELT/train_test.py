import requests
import sys

url = 'http://127.0.0.1:5000/api/train'

user_id = "Sh7sIjpW7DWrciOZchBjp81RwPD2"
model = sys.argv[1]

response = requests.post(url, json={'user_id': user_id, "model": model})

if response.text:
    res = response.json()

    print("Response Status Code:", response.status_code)
    print("Message:", res['message'])
    print("Accuracy:", res['accuracy'])
    print("Duration:", res['duration'])
else:
    print("Empty response")
