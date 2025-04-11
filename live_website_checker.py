import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys
import json
import warnings
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import joblib
import numpy as np
from tensorflow.keras.models import load_model

warnings.filterwarnings("ignore", category=UserWarning)

# Paths
log_path = Path("logs/prediction-log.json")
log_path.parent.mkdir(exist_ok=True)

# Load model and scaler
model = load_model("bug_predictor_model.keras")
scaler = joblib.load("bug_scaler.save")

def run_bug_check(url, selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        start_time = datetime.now()

        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(3000)

            headline_text = ""
            if selector and page.locator(selector).count() > 0:
                headline_text = page.locator(selector).first.inner_text().strip()
            elif page.locator("h1").count() > 0:
                headline_text = page.locator("h1").first.inner_text().strip()
            elif page.locator(".titlelink").count() > 0:
                headline_text = page.locator(".titlelink").first.inner_text().strip()

            headline_length = len(headline_text)
            missing_elements = 0 if headline_text else 1

        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
            return
        finally:
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            browser.close()

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

    try:
        if log_path.exists():
            with open(log_path, "r") as f:
                existing_logs = json.load(f)
        else:
            existing_logs = []

        existing_logs.append(result)

        with open(log_path, "w") as f:
            json.dump(existing_logs, f, indent=2)

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"⚠️ Failed to log result: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 live_website_checker.py <URL> [optional selector]")
    else:
        run_bug_check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
