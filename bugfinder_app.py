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
PREDICTION_LOG_PATH = "prediction-log.json"

def load_logs(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

def log_prediction(entry):
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(log_file_path, "w") as f:
        json.dump(data, f, indent=2)

def suggest_fix(entry):
    suggestions = []

    if entry.get("missingElements", 0) == 1:
        suggestions.append("🛠️ Consider adding a `<h1>` tag to clearly label the main heading of the page.")

    if entry.get("loadTimeMs", 0) > 3000:
        suggestions.append("⏳ Load time is high. Optimize images, scripts, or server response times.")

    if entry.get("headlineLength", 0) < 10:
        suggestions.append("🔤 Headline might be too short or empty. Check content generation or rendering.")

    if not suggestions:
        suggestions.append("✅ No obvious issues detected. Your page looks good!")

    return suggestions

tabs = st.tabs(["📊 Dashboard", "📁 Upload Logs", "🌐 Live Website Test"])

with tabs[0]:
    st.header("📈 Bug Detection Insights")
    df = load_logs(log_file_path)

    if df.empty:
        st.info("No prediction logs found. Please upload a file in the next tab.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed', errors='coerce')
        df = df.dropna(subset=["timestamp"])
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Bug Likelihood Over Time")
            plt.figure()
            plt.plot(df["timestamp"], df["prediction"], marker="o")
            plt.xticks(rotation=45)
            plt.ylabel("Bug Likelihood")
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
        plt.ylabel("Number of Tests")
        st.pyplot(plt)

with tabs[1]:
    st.header("📂 Upload New prediction-log.json")
    uploaded_file = st.file_uploader("Upload your new prediction-log.json", type=["json"])
    if uploaded_file is not None:
        new_data = json.load(uploaded_file)
        with open(log_file_path, "w") as f:
            json.dump(new_data, f, indent=2)
        st.success("✅ Log file updated! Go back to the Dashboard tab to see updated charts.")

with tabs[2]:
    st.subheader("🌐 Live Website Test")

    url = st.text_input("Enter a URL to test", placeholder="https://example.com")

    if st.button("Run Bug Check"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Running bug check on the website..."):
                try:
                    result = subprocess.run(
                        ["python3", "live_website_checker.py", url],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    st.code(result.stdout)
                    # Reload the updated log
                    with open(PREDICTION_LOG_PATH, "r") as f:
                        log_data = json.load(f)
                    st.success("Test complete and prediction-log.json updated!")

                    # Suggest fixes
                    if log_data:
                        last_result = log_data[-1]
                        fixes = suggest_fix(last_result)
                        st.markdown("### 🧠 Suggested Fixes:")
                        for fix in fixes:
                            st.markdown(f"- {fix}")

                except Exception as e:
                    st.error(f"Something went wrong: {e}")
