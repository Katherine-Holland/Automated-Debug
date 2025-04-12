import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="AI Bug Finder", layout="wide")
st.title("🕷️ AI-Powered Bug Finder")

log_file_path = os.path.join(os.path.dirname(__file__), "prediction-log.json")
st.info("✅ Streamlit app loaded successfully.")

# --- Utils ---

def load_logs(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return pd.DataFrame(json.load(f))
        except json.JSONDecodeError:
            return pd.DataFrame()
    return pd.DataFrame()

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

# --- Tabs ---
tabs = st.tabs(["🌐 Live Website Test", "📊 Dashboard", "📁 Upload Logs"])

# === TAB 1: Live Website Test ===
with tabs[0]:
    st.subheader("🌐 Live Website Test")
    url = st.text_input("Enter a URL to test", placeholder="https://example.com")

    if st.button("Run Bug Check"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Running bug checker..."):
                try:
                    result = subprocess.run(
                        ["python3", "live_website_checker.py", url],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    st.success("✅ Test complete!")
                    st.code(result.stdout)  # Optional: show stdout
                    # st.code(result.stderr)  # Optional: hide or show stderr

                    if os.path.exists(log_file_path):
                        with open(log_file_path, "r") as f:
                            log_data = json.load(f)

                        if log_data:
                            last = log_data[-1]
                            st.subheader("🆕 Last Result")
                            st.json(last)

                            st.markdown("### 💡 Suggested Fixes")
                            for fix in suggest_fix(last):
                                st.markdown(f"- {fix}")
                        else:
                            st.warning("No results found in log.")
                    else:
                        st.error("❌ prediction-log.json not found.")

                except Exception as e:
                    st.error(f"❌ Error running test: {e}")

# === TAB 2: Dashboard ===
with tabs[1]:
    st.header("📈 Bug Detection Insights")

    if st.button("🔁 Refresh Dashboard"):
        st.rerun()

    df = load_logs(log_file_path)

    if df.empty:
        st.info("No logs available.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed', errors='coerce')
        df = df.dropna(subset=["timestamp"])

        # Optional preview for debugging
        st.markdown("#### 📄 Latest Entries")
        st.dataframe(df.tail())

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📉 Bug Likelihood Over Time")
            plt.figure()
            plt.plot(df["timestamp"], df["prediction"], marker="o")
            plt.xticks(rotation=45)
            plt.ylabel("Bug Likelihood")
            plt.tight_layout()
            st.pyplot(plt)

        with col2:
            st.subheader("⏱️ Page Load Time Distribution")
            plt.figure()
            plt.hist(df["loadTimeMs"], bins=10, color="orange", edgecolor="black")
            plt.xlabel("Load Time (ms)")
            plt.ylabel("Frequency")
            st.pyplot(plt)

        st.subheader("✅ Test Outcome Summary")
        outcome_counts = df["result"].value_counts()
        plt.figure()
        outcome_counts.plot(kind="bar", color=["green", "red"])
        plt.ylabel("Number of Tests")
        st.pyplot(plt)
    
        with st.expander("⚙️ Admin Tools"):
            if st.button("🧹 Clear All Logs (Reset Dashboard)"):
                with open(log_path, "w") as f:
                    json.dump([], f, indent=2)
                st.success("✅ Dashboard logs cleared! Click refresh to update.")

# === TAB 3: Upload Logs ===
with tabs[2]:
    st.header("📁 Upload New prediction-log.json")
    uploaded_file = st.file_uploader("Upload your new prediction-log.json", type=["json"])
    if uploaded_file:
        try:
            new_data = json.load(uploaded_file)
            with open(log_file_path, "w") as f:
                json.dump(new_data, f, indent=2)
            st.success("✅ Log file updated!")
        except Exception as e:
            st.error(f"❌ Failed to load uploaded JSON: {e}")