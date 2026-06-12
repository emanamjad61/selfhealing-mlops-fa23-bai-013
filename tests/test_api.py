import os

import requests

BASE_URL = os.getenv("BASE_URL", "http://20.244.49.37:32500")


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_version" in data


def test_predict_returns_label_and_confidence():
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"text": "Spotlessly clean rooms with attentive staff and superb amenities throughout"},
        timeout=20,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] in ["POSITIVE", "NEGATIVE"]
    assert 0 <= data["confidence"] <= 1
    assert "model_version" in data


def test_predict_negative_text():
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"text": "The hotel was terrible, awful, and the worst experience"},
        timeout=20,
    )
    assert response.status_code == 200


def test_health_returns_model_version_unstable():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["model_version"] == "unstable-v1"
