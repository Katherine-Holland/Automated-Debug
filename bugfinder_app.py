import sys
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright
import joblib
import numpy as np
from tensorflow.keras.models import load_model
os.system('playwright install')
os.system('playwright install-deps')

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
            page.wait_for_timeout(3000)  # Wait a moment for content to load

            headline_text = ""

            # Try custom selector if provided
            if selector:
                if page.locator(selector).count() > 0:
                    headline_text = page.locator(selector).first.inner_text().strip()
            else:
                # Fallback sequence
                for fallback_selector in ["h1", ".titlelink", "header h1", "title"]:
                    if page.locator(fallback_selector).count() > 0:
                        headline_text = page.locator(fallback_selector).first.inner_text().strip()
                        break

            headline_length = len(headline_text)
            missing_elements = 0 if headline_text else 1

        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
            return
        finally:
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            browser.close()

    # Prepare input for prediction
    inputs = scaler.transform([[headline_length, load_time, missing_elements]])
    prediction = model.predict(inputs)[0][0]

    # Compose log entry
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "url": url,
        "selector": selector if selector else "Auto (h1/fallback)",
        "headlineLength": headline_length,
        "loadTimeMs": round(load_time),
        "missingElements": missing_elements,
        "prediction": round(float(prediction), 4),
        "result": "ran test"
    }

    # Save to log
    log_path = "prediction-log.json"
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                existing_logs = json.load(f)
        else:
            existing_logs = []

        existing_logs.append(result)

        with open(log_path, "w") as f:
            json.dump(existing_logs, f, indent=2)

        # Print result
        print(f"\n✅ Checked: {url}")
        print(f"📌 Selector used: {result['selector']}")
        print(f"🧠 Headline Length: {headline_length}")
        print(f"⏱️ Load Time: {round(load_time)} ms")
        print(f"❓ Missing Element: {'Yes' if missing_elements else 'No'}")
        print(f"🤖 Bug Likelihood: {round(float(prediction), 4)}")

    except Exception as e:
        print(f"⚠️ Failed to log result: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 live_website_checker.py <URL> [optional CSS selector]")
    else:
        url = sys.argv[1]
        selector = sys.argv[2] if len(sys.argv) > 2 else None
        run_bug_check(url, selector)
