import requests


headers = {
    "Origin": "http://example.com",
}

response = requests.get("http://localhost:8000/", headers=headers)

print("Response Code:", response.status_code)
print("Response Headers:", response.headers)
print("Response Body:", response.json())
