import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="AI Bug Finder", layout="wide")
st.title("🕷️ AI-Powered Bug Finder Dashboard")

log_file_path = "prediction-log.json"

st.info("✅ Streamlit app loaded successfully.")

# Load logs
def load_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

def suggest_fix(entry):
    suggestions = []
    if entry.get("missingElements", 0) == 1:
        suggestions.append("🛠️ Consider adding a `<h1>` tag.")
    if entry.get("loadTimeMs", 0) > 3000:
        suggestions.append("⏳ Load time is high. Optimize resources.")
    if entry.get("headlineLength", 0) < 10:
        suggestions.append("🔤 Headline may be too short or missing.")
    if not suggestions:
        suggestions.append("✅ No issues found.")
    return suggestions

tabs = st.tabs(["📊 Dashboard", "📁 Upload Logs", "🌐 Live Website Test"])

# --- Dashboard
with tabs[0]:
    st.header("📈 Bug Detection Insights")
    if st.button("🔁 Refresh Dashboard"):
        st.rerun()

    df = load_logs()

    if df.empty:
        st.info("No logs yet. Please run a test or upload a file.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Bug Likelihood Over Time")
            plt.figure()
            plt.plot(df["timestamp"], df["prediction"], marker="o")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

        with col2:
            st.subheader("Page Load Time Distribution")
            plt.figure()
            plt.hist(df["loadTimeMs"], bins=10, color="orange", edgecolor="black")
            plt.xlabel("Load Time (ms)")
            plt.ylabel("Frequency")
            st.pyplot(plt)

        st.subheader("Test Outcome Summary")
        outcome_counts = df["result"].value_counts()
        plt.figure()
        outcome_counts.plot(kind="bar", color=["green", "red"])
        plt.ylabel("Test Count")
        st.pyplot(plt)

# --- Upload Logs
with tabs[1]:
    st.header("📂 Upload prediction-log.json")
    uploaded_file = st.file_uploader("Upload prediction-log.json", type=["json"])
    if uploaded_file:
        new_data = json.load(uploaded_file)
        with open(log_file_path, "w") as f:
            json.dump(new_data, f, indent=2)
        st.success("✅ Log updated! Go to the dashboard tab.")

# --- Live Test
with tabs[2]:
    st.header("🌐 Live Website Test")
    url = st.text_input("Enter a URL", placeholder="https://example.com")
    if st.button("Run Bug Check"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Running check..."):
                result = subprocess.run(
                    ["python3", "live_website_checker.py", url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                st.code(result.stdout)
                st.code(result.stderr)

                if os.path.exists(log_file_path):
                    with open(log_file_path, "r") as f:
                        logs = json.load(f)
                        last = logs[-1]
                        st.subheader("🆕 Last Result")
                        st.json(last)

                        fixes = suggest_fix(last)
                        st.markdown("### 💡 Suggested Fixes:")
                        for fix in fixes:
                            st.markdown(f"- {fix}")
                else:
                    st.warning("No log file found after test.")
