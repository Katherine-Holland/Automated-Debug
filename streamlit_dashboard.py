import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

st.set_page_config(page_title="AI Bug Dashboard", layout="wide")

st.title("🤖 Automated Debug Dashboard")
st.markdown("View insights from AI-driven bug detection based on Playwright test logs.")

# Upload section
uploaded_file = st.file_uploader("Upload your prediction-log.json", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    df = pd.DataFrame(data)

    # Convert timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    st.success("✅ File loaded successfully!")

    # Charts
    st.subheader("📈 Bug Likelihood Over Time")
    fig1, ax1 = plt.subplots()
    ax1.plot(df["timestamp"], df["prediction"], marker='o')
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Bug Likelihood")
    ax1.grid(True)
    st.pyplot(fig1)

    st.subheader("⏱️ Load Time Distribution (ms)")
    fig2, ax2 = plt.subplots()
    ax2.hist(df["loadTimeMs"], bins=10, color="skyblue", edgecolor="black")
    ax2.set_xlabel("Load Time (ms)")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

    st.subheader("📊 Test Outcome Summary")
    fig3, ax3 = plt.subplots()
    df["result"].value_counts().plot(kind="bar", ax=ax3, color=["green", "orange"])
    ax3.set_ylabel("Count")
    st.pyplot(fig3)

    # Raw data preview
    with st.expander("📋 View Raw Data"):
        st.dataframe(df)
else:
    st.warning("👆 Upload a `prediction-log.json` file to begin.")
