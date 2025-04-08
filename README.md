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
├── playwright.config.js           # Playwright configuration file
└── tests/
    └── bugChecker.spec.js         # Our main test script
```

---

## 🚀 Running the Test

To execute the script:
```bash
npx playwright test
```

If the headline on Hacker News is shorter than expected, the test fails and saves a screenshot like this:

![Bug Screenshot Example](./error-screenshot.png)

> ✅ If the headline is valid, the test will simply pass.

---

## 🧪 What the Script Does

1. Opens [https://news.ycombinator.com](https://news.ycombinator.com)
2. Extracts the first post headline
3. Checks its length (we set an intentionally high threshold to simulate bugs)
4. On failure:
   - Takes a screenshot
   - Fails the test
   - Saves full trace and video (great for debugging!)

---

## 🔍 Bonus Debugging Tools

After a failed run, Playwright also stores:
- 📸 `test-results/` folder with screenshots and videos
- 🕵️ A trace file you can view with:

```bash
npx playwright show-trace test-results/<your-trace-file>.zip
```

---

## 🤖 AI-Powered Bug Prediction

We've trained a TensorFlow model to predict bugs before they even happen!

This model takes three real-time features:
- `headlineLength`
- `loadTimeMs`
- `missingElements`

And estimates the likelihood of a bug occurring. If the prediction is **below a certain threshold**, the test will automatically **skip** to save time and resources.

### 🧠 How It Works
1. A Python script (`predictor_bridge.py`) loads the trained AI model.
2. It accepts input from the Playwright test (e.g., `18 1600 2`) and returns a prediction score.
3. If the predicted likelihood is high (e.g., > 0.5), the test proceeds and validates the page.
4. If the likelihood is low, the test logs it and skips!

### Example Output:

```bash
🔍 Raw prediction output: 0.6215
🤖 AI Prediction: Bug Likelihood = 0.62
✅ AI predicts no bug — skipping test.
```

> You can adjust the threshold logic in `bugChecker.spec.js` to suit your use case.

---

## 📁 Additional Files

```
.
├── bug_predictor_model.keras      # Trained AI model (TensorFlow)
├── bug_scaler.save                # Scaler for input normalization
├── predictor_bridge.py            # Python bridge script for predictions
├── train_bug_predictor.py         # Train your own model on synthetic data
├── synthetic_bug_data.csv         # Dataset used for model training
```

---

## 🧠 Training Your Own AI Model

Want to re-train the bug predictor? Run:

```bash
python train_bug_predictor.py
```

This will:
- Load `synthetic_bug_data.csv`
- Train a neural network
- Save the model and scaler
