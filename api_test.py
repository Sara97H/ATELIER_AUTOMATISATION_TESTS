import requests
import time

def test_api():
    start = time.time()
    response = requests.get("https://api.agify.io/?name=mari")
    duration = time.time() - start

    return {
        "status_code": response.status_code,
        "response_time": round(duration, 3),
        "available": response.status_code == 200
    }
