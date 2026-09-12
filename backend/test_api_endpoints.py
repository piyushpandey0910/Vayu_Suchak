import sys
import os

# UTF-8 output encoding for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

def run_tests():
    print("=" * 60)
    print("RUNNING VAYU SUCHAK API VERIFICATION TESTS")
    print("=" * 60)

    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print("[PASS] 1. Root health check: OK")

        # 2. Current AQI
        res = client.get("/api/aqi/current?city=Kanpur")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert "aqi" in data and "pm25" in data and "pollutants" in data
        print(f"[PASS] 2. Current AQI for {data['city']}: AQI={data['aqi']}, Status={data['category']}")

        # 3. Forecast
        res = client.get("/api/aqi/forecast?city=Kanpur&hours=24")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert len(data["points"]) == 24
        print(f"[PASS] 3. Forecast 24h: {len(data['points'])} points, Mean AQI={data['average_predicted_aqi']}")

        # 4. History
        res = client.get("/api/aqi/history?city=Kanpur&range=7d")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert len(data["points"]) > 0
        print(f"[PASS] 4. History 7d: {len(data['points'])} records loaded")

        # 5. Pollutants
        res = client.get("/api/aqi/pollutants?city=Kanpur")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert "pm25" in data["pollutants"] and "co" in data["pollutants"]
        print(f"[PASS] 5. Pollutants breakdown: {list(data['pollutants'].keys())}")

        # 6. Health Advisory
        res = client.get("/api/health-advisory?aqi=145")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["category"] == "Unhealthy for Sensitive Groups"
        print(f"[PASS] 6. Health Advisory (AQI 145): {data['headline']}")

        # 7. AI Health Assistant Chat
        res = client.post("/api/ai/chat", json={
            "message": "Can I go jogging outside today?",
            "city": "Kanpur",
            "current_aqi": 145
        })
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert "reply" in data and len(data["reply"]) > 20
        print(f"[PASS] 7. AI Health Chat: reply received from {data['source']}")

        # 8. Location Search
        res = client.get("/api/locations/search?q=kan")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert len(data["results"]) > 0
        print(f"[PASS] 8. Location search query 'kan': found {len(data['results'])} matches")

        # 9. Auth Status (Placeholder)
        res = client.get("/api/auth/status")
        assert res.status_code == 200
        data = res.json()
        assert data["auth_enabled"] is False
        print(f"[PASS] 9. Auth placeholder status: {data['mode']}")

        # 10. Rate limiting test
        print("Testing rate limiter on /api/ai/chat (exceeding 10/min)...")
        rate_limited = False
        for i in range(12):
            r = client.post("/api/ai/chat", json={"message": f"ping {i}", "city": "Kanpur", "current_aqi": 100})
            if r.status_code == 429:
                rate_limited = True
                print(f"[PASS] 10. Rate limiter triggered successfully at call {i+1} with HTTP 429: {r.json()['message']}")
                break
        assert rate_limited, "Expected rate limit to trigger on rapid requests"

    print("=" * 60)
    print("ALL 10 API AND RATE LIMIT VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
