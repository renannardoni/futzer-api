import requests

BASE_URL = "http://localhost:8000/api"

try:
    r = requests.get(f"{BASE_URL}/quadras/")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Quadras:", r.json())
    else:
        print("Error:", r.text)
except Exception as e:
    print(f"Erro na request: {e}")
