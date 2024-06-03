import requests

url = 'http://127.0.0.1:5000/api/train'

response = requests.post(url)
print(response.content)
print('Response Status Code:', response.status_code)