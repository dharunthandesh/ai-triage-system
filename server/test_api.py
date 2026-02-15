import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Test Health
    try:
        resp = requests.get(f"{BASE_URL}/api/health")
        if resp.status_code == 200:
            print("✅ Health Check Passed")
        else:
            print(f"❌ Health Check Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return

    # 2. Test Prediction
    payload = {
        "age": 45,
        "gender": "Male",
        "heart_rate": 80,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "temperature": 37.0,
        "symptom": "Chest Pain",
        "history": "None"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/predict", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Prediction Check Passed")
            print(f"   Risk: {data.get('risk_level')}")
            print(f"   Dept: {data.get('department')}")
            print(f"   Conf: {data.get('confidence_score')}")
        else:
            print(f"❌ Prediction Check Failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ Prediction Check Error: {e}")

if __name__ == "__main__":
    test_api()
