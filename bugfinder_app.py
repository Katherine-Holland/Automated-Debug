import streamlit as st
import subprocess
import json
import base64
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="BugFinder AI", layout="centered")

st.title("🕷️ BugFinder AI – Automated Bug Scanner")
st.markdown("Enter a website URL to scan for potential issues using Playwright and AI.")

url = st.text_input("🔗 Enter Website URL", "https://news.ycombinator.com")
run_button = st.button("🚀 Scan Site")

if run_button:
    with st.spinner("Running bug checks..."):
        # 1. Run Playwright test with dynamic URL
        result = subprocess.run(
            ["npx", "playwright", "test", f"tests/bugChecker.spec.js", f'--project=chromium', f'--grep=^{url}$'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        st.code(result.stdout, language="bash")

        # 2. Load prediction-log.json
        log_path = Path("prediction-log.json")
        if log_path.exists():
            logs = json.loads(log_path.read_text())
            latest = logs[-1]

            st.subheader("🧠 AI Prediction Results")
            st.metric("Bug Likelihood", f"{latest['prediction']:.2f}")
            st.json(latest)

            # 3. Show Screenshot
            screenshot = Path("error-screenshot.png")
            if screenshot.exists():
                st.image(Image.open(screenshot), caption="Bug Screenshot")

            # 4. Downloadable Report
            report_json = json.dumps(latest, indent=2)
            b64 = base64.b64encode(report_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="bug-report.json">📄 Download Bug Report</a>'
            st.markdown(href, unsafe_allow_html=True)

        else:
            st.warning("No prediction log found. Did the test complete correctly?")
