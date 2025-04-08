const { test, expect } = require('@playwright/test');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

test('Check Hacker News headlines and take screenshot if bug found', async ({ page }) => {
  const start = Date.now();
  await page.goto('https://news.ycombinator.com');
  const loadTimeMs = Date.now() - start;

  // Get actual headline length
  const headlineElement = await page.locator('.athing').first();
  const headlineText = await headlineElement.innerText();
  const headlineLength = headlineText.length;

  // Count missing expected elements
  let missingElements = 0;
  const expectedSelectors = ['.title', '.subtext', '.score'];
  for (const selector of expectedSelectors) {
    const count = await page.locator(selector).count();
    if (count === 0) missingElements++;
  }

  console.log(`🧠 Inputs → headlineLength: ${headlineLength}, loadTimeMs: ${loadTimeMs}, missingElements: ${missingElements}`);

  // Run AI prediction
  const rawPrediction = execSync(`python3 predictor_bridge.py ${headlineLength} ${loadTimeMs} ${missingElements}`);
  const prediction = rawPrediction.toString().trim();
  const match = prediction.match(/[\d.]+/);
  const likelihood = match ? parseFloat(match[0]) : NaN;

  if (isNaN(likelihood)) {
    console.warn("⚠️ Could not parse AI prediction. Skipping test.");
    return;
  }

  console.log(`🤖 AI Prediction: Bug Likelihood = ${likelihood.toFixed(2)}`);

  // Log prediction
  const logEntry = {
    headlineLength,
    loadTimeMs,
    missingElements,
    prediction: likelihood,
    result: likelihood < 0.3 ? "skipped" : "ran test",
    timestamp: new Date().toISOString()
  };

  const logPath = path.join(__dirname, '..', 'prediction-log.json');
  let logData = [];

  try {
    if (fs.existsSync(logPath)) {
      const existing = fs.readFileSync(logPath);
      logData = JSON.parse(existing);
    }
  } catch (err) {
    console.error('Could not read existing log:', err);
  }

  logData.push(logEntry);

  try {
    fs.writeFileSync(logPath, JSON.stringify(logData, null, 2));
    console.log('📝 Logged prediction to prediction-log.json');
  } catch (err) {
    console.error('❌ Failed to write log file:', err);
  }

  // Skip test if prediction is low
  if (likelihood < 0.3) {
    console.log('✅ AI predicts no bug — skipping test.');
    return;
  }

  // Final test: is the headline valid?
  if (!headlineText || headlineText.length < 10) {
    await page.screenshot({ path: 'error-screenshot.png' });
    throw new Error('Bug detected: Headline is too short or missing');
  }

  expect(headlineText.length).toBeGreaterThan(10);
});
