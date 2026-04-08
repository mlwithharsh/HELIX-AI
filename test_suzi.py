import requests
import json

url = "http://localhost:8000/api/chat"
payload = {
    "message": "Hey Suzi, what are you doing right now?",
    "personality": "suzi"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
