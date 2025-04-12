import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys
import json
import warnings
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess

warnings.filterwarnings("ignore")
sys.stderr = open(os.devnull, 'w')

st.set_page_config(page_title="AI Bug Finder", layout="wide")
st.title("🕷️ AI Bug Finder - Full Report")

log_path = os.path.join(os.path.dirname(__file__), "prediction-log.json")

def load_logs(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return pd.DataFrame(json.load(f))
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def suggest_fix(entry):
    suggestions = []
    if entry.get("missingElements", 0): suggestions.append("🛠️ Add a `<h1>` tag.")
    if entry.get("loadTimeMs", 0) > 3000: suggestions.append("⏳ Improve load speed.")
    if entry.get("headlineLength", 0) < 10: suggestions.append("🔤 Headline may be unclear.")
    if entry.get("jsErrors"): suggestions.append(f"❌ JS errors found: {len(entry['jsErrors'])}")
    if entry.get("brokenResources"): suggestions.append(f"🚫 Broken resources: {len(entry['brokenResources'])}")
    return suggestions or ["✅ No obvious issues detected."]

# === LIVE CHECK + DASHBOARD TAB ===
st.subheader("🌐 Live Website Test + Report")

url = st.text_input("Enter a URL to test", placeholder="https://example.com")
if st.button("Run Bug Check"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Running test..."):
            result = subprocess.run(
                ["python3", "live_website_checker.py", url],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            st.code(result.stdout)
            st.code(result.stderr)

df = load_logs(log_path)
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df = df.dropna(subset=["timestamp"])
    df["domain"] = df["url"].apply(lambda x: x.split("/")[2] if "://" in x else x)
    df["shortUrl"] = df["url"].apply(lambda x: x.replace("https://", "").replace("http://", ""))

    selected_domain = st.selectbox("Select a domain", df["domain"].unique())
    filtered = df[df["domain"] == selected_domain].sort_values("timestamp")

    st.subheader(f"🔎 Domain: {selected_domain}")
    st.dataframe(filtered[["timestamp", "shortUrl", "prediction", "loadTimeMs", "missingElements"]])

    entry_url = st.selectbox("Select a URL for full debug info", filtered["shortUrl"].tolist())
    latest_entry = filtered[filtered["shortUrl"] == entry_url].iloc[-1].to_dict()
    st.subheader("📋 Detailed Debug Info")
    st.json(latest_entry)

    st.markdown("### 📈 Bug Likelihood Over Time")
    plt.figure()
    plt.plot(filtered["timestamp"], filtered["prediction"], marker="o")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    st.markdown("### ⏱️ Load Time Distribution")
    plt.figure()
    plt.hist(filtered["loadTimeMs"], bins=10, color="orange", edgecolor="black")
    st.pyplot(plt)

    st.markdown("### 📊 Test Result Summary")
    outcome_counts = filtered["result"].value_counts()
    plt.figure()
    outcome_counts.plot(kind="bar", color="green")
    st.pyplot(plt)

    st.markdown("### 💡 Suggested Fixes")
    for fix in suggest_fix(latest_entry):
        st.markdown(f"- {fix}")
else:
    st.info("Run a test to see data here.")
