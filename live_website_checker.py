import sys
import os
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import joblib
import numpy as np
from tensorflow.keras.models import load_model

# Load model and scaler
model = load_model("bug_predictor_model.keras")
scaler = joblib.load("bug_scaler.save")

def run_bug_check(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        start_time = datetime.now()

        try:
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle")  # Wait for full load
            page.wait_for_timeout(2000)

            headline = page.locator("h1").first
            headline_text = headline.inner_text() if headline.count() > 0 else ""
            headline_length = len(headline_text.strip())
            missing_elements = 0 if headline_text else 1

        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
            headline_length = 0
            missing_elements = 1

        finally:
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            browser.close()

    # Make prediction
    inputs = scaler.transform([[headline_length, load_time, missing_elements]])
    prediction = model.predict(inputs)[0][0]
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "url": url,
        "headlineLength": headline_length,
        "loadTimeMs": round(load_time),
        "missingElements": missing_elements,
        "prediction": round(float(prediction), 4),
        "result": "ran test"
    }

    # Log result
    log_path = "prediction-log.json"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            existing_logs = json.load(f)
    else:
        existing_logs = []

    existing_logs.append(result)

    with open(log_path, "w") as f:
        json.dump(existing_logs, f, indent=2)

    # Print result
    print(f"\n✅ Checked {url}")
    print(f"🧠 Headline Length: {headline_length}")
    print(f"⏱️ Load Time: {round(load_time)} ms")
    print(f"❓ Missing h1: {'Yes' if missing_elements else 'No'}")
    print(f"🤖 Bug Likelihood: {round(float(prediction), 4)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 live_website_checker.py <URL>")
    else:
        run_bug_check(sys.argv[1])
