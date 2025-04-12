import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs

import sys
import json
import warnings
from urllib.parse import urlparse
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)
sys.stderr = open(os.devnull, 'w')  # Mute stderr

import joblib
import numpy as np
from playwright.sync_api import sync_playwright
from tensorflow.keras.models import load_model

model = load_model("bug_predictor_model.keras")
scaler = joblib.load("bug_scaler.save")

def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except:
        return "unknown"

def run_bug_check(url, selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        start_time = datetime.now()

        js_errors = []
        broken_resources = []

        page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: broken_resources.append({
            "url": req.url,
            "error": req.failure
        }))

        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(3000)

            headline_text = ""
            if selector and page.locator(selector).count() > 0:
                headline_text = page.locator(selector).first.inner_text().strip()
            else:
                for tag in ["h1", ".titlelink", "header h1", "title"]:
                    if page.locator(tag).count() > 0:
                        headline_text = page.locator(tag).first.inner_text().strip()
                        break

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
        "domain": extract_domain(url),
        "selector": selector or "Auto (h1/fallback)",
        "headlineLength": headline_length,
        "loadTimeMs": round(load_time),
        "missingElements": missing_elements,
        "jsErrors": js_errors,
        "brokenResources": broken_resources,
        "prediction": round(float(prediction), 4),
        "result": "ran test"
    }

    try:
        log_path = "prediction-log.json"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                existing = json.load(f)
        else:
            existing = []

        existing.append(result)
        with open(log_path, "w") as f:
            json.dump(existing, f, indent=2)

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"⚠️ Logging error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 live_website_checker.py <URL> [optional selector]")
    else:
        run_bug_check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
