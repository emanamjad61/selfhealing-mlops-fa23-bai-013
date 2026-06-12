import os
import time

import requests
from prometheus_client import Gauge, start_http_server

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:32500/api/latest-confidence")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "8000"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))

confidence_gauge = Gauge(
    "prediction_confidence_score",
    "Latest sentiment model prediction confidence score",
)


def get_confidence():
    try:
        response = requests.get(APP_URL, timeout=3)
        response.raise_for_status()
        value = float(response.json().get("confidence", 1.0))
        if 0.0 <= value <= 1.0:
            return value
    except Exception:
        pass
    return 1.0


def main():
    start_http_server(EXPORTER_PORT)
    while True:
        confidence_gauge.set(get_confidence())
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
