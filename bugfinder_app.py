import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import subprocess
from urllib.parse import urlparse
from datetime import datetime

st.set_page_config(page_title="AI Bug Finder", layout="wide")
st.title("🕷️ AI-Powered Bug Finder Dashboard")

log_path = os.path.join(os.path.dirname(__file__), "prediction-log.json")
st.info("✅ Streamlit app loaded successfully.")

# --- UTILS ---

def load_logs(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return pd.DataFrame(json.load(f))
        except json.JSONDecodeError:
            return pd.DataFrame()
    return pd.DataFrame()

def extract_domain(url):
    parsed = urlparse(url)
    return parsed.netloc

def suggest_fix(entry):
    suggestions = []
    if entry.get("missingElements", 0) == 1:
        suggestions.append("🛠️ Consider adding a `<h1>` tag.")
    if entry.get("loadTimeMs", 0) > 3000:
        suggestions.append("⏳ Optimize load performance.")
    if entry.get("headlineLength", 0) < 10:
        suggestions.append("🔤 Improve headline clarity.")
    if not suggestions:
        suggestions.append("✅ No obvious issues detected.")
    return suggestions

# === TABS ===
tabs = st.tabs(["🌐 Live Website Test", "📊 Dashboard", "📁 Upload Logs"])

# === TAB 1: LIVE TEST ===
with tabs[0]:
    st.subheader("🌐 Live Website Test")
    url = st.text_input("Enter a URL to test", placeholder="https://example.com")

    if st.button("Run Bug Check"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Running test..."):
                try:
                    result = subprocess.run(
                        ["python3", "live_website_checker.py", url],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    st.code(result.stdout)
                    st.code(result.stderr)

                    if os.path.exists(log_path):
                        with open(log_path, "r") as f:
                            log_data = json.load(f)
                        st.success("✅ Test complete!")

                        last_result = log_data[-1]
                        st.subheader("🆕 Last Result")
                        st.json(last_result)

                        st.markdown("### 💡 Suggested Fixes")
                        for fix in suggest_fix(last_result):
                            st.markdown(f"- {fix}")
                    else:
                        st.warning("Log not found.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# === TAB 2: DASHBOARD ===
with tabs[1]:
    st.header("📊 Bug Detection Dashboard")

    if st.button("🔁 Refresh Dashboard"):
        st.rerun()

    df = load_logs(log_path)
    if df.empty:
        st.info("No logs available.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df["domain"] = df["url"].apply(extract_domain)

        grouped = df.groupby("domain")

        selected_domain = st.selectbox("🔎 Select domain to view:", grouped.groups.keys())
        domain_df = grouped.get_group(selected_domain)

        st.dataframe(domain_df[["timestamp", "url", "prediction", "loadTimeMs", "headlineLength"]].sort_values("timestamp", ascending=False))

        st.subheader(f"📉 Bug Likelihood for {selected_domain}")
        plt.figure()
        plt.plot(domain_df["timestamp"], domain_df["prediction"], marker="o")
        plt.xticks(rotation=45)
        plt.ylabel("Bug Likelihood")
        st.pyplot(plt)

        st.subheader("⏱️ Load Time")
        plt.figure()
        plt.hist(domain_df["loadTimeMs"], bins=10, color="orange", edgecolor="black")
        st.pyplot(plt)

# === TAB 3: UPLOAD LOG FILE ===
with tabs[2]:
    st.header("📁 Upload prediction-log.json")
    uploaded_file = st.file_uploader("Upload your new prediction-log.json", type=["json"])
    if uploaded_file:
        new_data = json.load(uploaded_file)
        with open(log_path, "w") as f:
            json.dump(new_data, f, indent=2)
        st.success("✅ Log file updated!")
