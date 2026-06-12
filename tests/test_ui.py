import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.getenv("BASE_URL", "http://20.244.49.37:32500")


def test_frontend_sentiment():
    options = Options()
    options.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(BASE_URL)
        text_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        text_input.send_keys("Spotlessly clean rooms with attentive staff and superb amenities throughout")
        driver.find_element(By.ID, "submit-btn").click()
        result = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "result-output"))
        )
        WebDriverWait(driver, 30).until(lambda _: result.text.strip())
        assert any(term in result.text for term in ["POSITIVE", "NEGATIVE", "Confidence"])
    finally:
        driver.quit()
