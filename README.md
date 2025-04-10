
# Automated-Debug

Uh oh! You have a web application that displays real-time data from multiple sources. Sometimes, the data fails to update correctly, or there are discrepancies in the values.  
Let's automate the detection of these issues, capture them with screenshots, and provide a summary of what might be causing the problem... lets throw in some Ai too 😉

This project uses [Microsoft Playwright](https://playwright.dev/) to automatically check the **Hacker News** homepage for potential headline issues. If a bug is detected (like a short or missing headline), a screenshot is captured automatically for debugging.

---

## 🛠️ Project Setup

### 1. Initialize your Node.js project
```bash
npm init -y
```

### 2. Install Playwright Test
```bash
npm install --save-dev @playwright/test
```

---

## 📂 Project Structure

```
.
├── playwright.config.js
├── bugfinder_app.py                # Streamlit dashboard
├── live_website_checker.py        # AI-powered URL tester
├── prediction-log.json            # Log file for all predictions
└── tests/
    └── bugChecker.spec.js         # Playwright test script
```

---

## 🚀 Running the Test

```bash
npx playwright test
```

If the headline on Hacker News is shorter than expected, the test fails and saves a screenshot like this:

![Bug Screenshot Example](./error-screenshot.png)

---

## 🤖 AI-Powered Bug Prediction

A trained TensorFlow model predicts bugs in real-time based on:
- `headlineLength`
- `loadTimeMs`
- `missingElements`

If the likelihood of a bug is high (> 0.5), the test continues. If low, it skips to save time.

---

## 🌐 Live AI Dashboard with Streamlit

```bash
streamlit run bugfinder_app.py
```

### Features:
- 📈 Bug likelihood over time
- ⏱️ Load time distribution
- 📊 Test outcome summary
- 📂 Upload new logs to refresh visuals
- 🔍 Test any live URL with bug prediction
- 🧠 AI-powered suggestions shown for each issue

---

## ✨ Example Suggestions from the AI

After testing a site, the system will offer fixes, like:

- 🛠️ Consider adding a `<h1>` tag to clearly label the main heading of the page.
- ⏳ Load time is high. Optimize images, scripts, or server response times.
- 🔤 Headline might be too short or empty. Check content generation or rendering.

These appear directly below each test result in the dashboard.

---

## 📁 Other AI Files

```
├── bug_predictor_model.keras      # Trained model
├── bug_scaler.save                # Scaler for normalization
├── predictor_bridge.py            # Python script used by Playwright
├── synthetic_bug_data.csv         # Training data
├── train_bug_predictor.py         # Training script
```

---

## 🔁 Training Your Own Model

```bash
python train_bug_predictor.py
```

---

## ✅ Python Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---