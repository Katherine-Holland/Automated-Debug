import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
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

def suggest_fix(entry):
    suggestions = []
    if entry.get("missingElements", 0) == 1:
        suggestions.append("🛠️ Consider adding a `<h1>` tag.")
    if entry.get("loadTimeMs", 0) > 3000:
        suggestions.append("⏳ Optimize load performance.")
    if entry.get("headlineLength", 0) < 10:
        suggestions.append("🔤 Improve headline clarity.")
    if entry.get("jsErrors"):
        suggestions.append(f"❌ JavaScript errors detected: {len(entry['jsErrors'])}")
    if entry.get("brokenResources"):
        suggestions.append(f"🚫 Broken resources found: {len(entry['brokenResources'])}")
    if not suggestions:
        suggestions.append("✅ No obvious issues detected.")
    return suggestions

# --- LOAD & CLEAN DATA ---
df = load_logs(log_path)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed', errors='coerce')
    df = df.dropna(subset=["timestamp"])

    # Safely extract shortUrl and domain
    df["shortUrl"] = df["url"].apply(lambda u: u.replace("https://", "").replace("http://", "") if isinstance(u, str) else "")
    df["domain"] = df["url"].apply(lambda u: u.split("//")[-1].split("/")[0] if isinstance(u, str) else "")

# --- TABS ---
tabs = st.tabs(["🌐 Live Website Test", "📊 Dashboard", "📁 Upload Logs"])

# === TAB 1: LIVE TEST ===
with tabs[0]:
    st.subheader("🌐 Live Website Test")
    url = st.text_input("Enter a URL to test", placeholder="https://example.com")

    if st.button("Run Bug Check"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Running bug test..."):
                import subprocess
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
                        logs = json.load(f)
                    if logs:
                        last_result = logs[-1]
                        st.success("✅ Test complete!")
                        st.subheader("🆕 Last Result")
                        st.json(last_result)

                        st.markdown("### 💡 Suggested Fixes")
                        for fix in suggest_fix(last_result):
                            st.markdown(f"- {fix}")
                else:
                    st.warning("⚠️ No prediction log file found.")

# === TAB 2: DASHBOARD ===
with tabs[1]:
    st.header("📈 Bug Detection Insights")

    if df.empty:
        st.info("No logs found. Please run a live test.")
    else:
        selected_domain = st.selectbox("Select a domain to explore", df["domain"].unique())
        domain_df = df[df["domain"] == selected_domain].sort_values("timestamp")

        st.subheader(f"🔍 Results for {selected_domain}")

        # Summary Table
        st.dataframe(
            domain_df[["timestamp", "shortUrl", "prediction", "loadTimeMs", "missingElements"]],
            use_container_width=True,
        )

        # Drilldown
        selected_row = st.selectbox(
            "Click below to inspect details for a test entry",
            domain_df["shortUrl"].tolist()
        )
        selected_entry = domain_df[domain_df["shortUrl"] == selected_row].iloc[-1].to_dict()
        st.subheader("🔎 Detailed Debug Info")
        st.json(selected_entry)

        st.markdown("### 📈 Bug Likelihood Over Time")
        plt.figure()
        plt.plot(domain_df["timestamp"], domain_df["prediction"], marker="o")
        plt.xticks(rotation=45)
        plt.ylabel("Bug Likelihood")
        plt.tight_layout()
        st.pyplot(plt)

        st.markdown("### ⏱️ Load Time Distribution")
        plt.figure()
        plt.hist(domain_df["loadTimeMs"], bins=10, color="orange", edgecolor="black")
        plt.xlabel("Load Time (ms)")
        plt.ylabel("Frequency")
        st.pyplot(plt)

        st.markdown("### ✅ Test Outcome Summary")
        outcome_counts = domain_df["result"].value_counts()
        plt.figure()
        outcome_counts.plot(kind="bar", color=["green", "red"])
        plt.ylabel("Number of Tests")
        st.pyplot(plt)

# === TAB 3: UPLOAD ===
with tabs[2]:
    st.header("📁 Upload a New prediction-log.json")
    uploaded_file = st.file_uploader("Upload your JSON log file", type=["json"])
    if uploaded_file:
        new_data = json.load(uploaded_file)
        with open(log_path, "w") as f:
            json.dump(new_data, f, indent=2)
        st.success("✅ Log file replaced. Refresh the app to view.")
