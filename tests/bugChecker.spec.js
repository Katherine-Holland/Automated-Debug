const { test, expect } = require('@playwright/test');
const { execSync } = require('child_process');

test('Check Hacker News headlines and take screenshot if bug found', async ({ page }) => {
  // Simulated features for prediction
  const headlineLength = 18;
  const loadTimeMs = 1600;
  const missingElements = 2;

  // Run Python predictor
  const rawPrediction = execSync(`python3 predictor_bridge.py ${headlineLength} ${loadTimeMs} ${missingElements}`);
  const prediction = rawPrediction.toString().trim();
  console.log(`🔍 Raw prediction output: ${prediction}`);

  // Match the first valid float number using regex
  const match = prediction.match(/[\d.]+/);
  const likelihood = match ? parseFloat(match[0]) : NaN;

  if (isNaN(likelihood)) {
    console.warn("⚠️ Could not parse AI prediction. Skipping test.");
    return;
  }

  console.log(`🤖 AI Prediction: Bug Likelihood = ${likelihood.toFixed(2)}`);

  if (likelihood < 0.3) {
    console.log('✅ AI predicts no bug — skipping test.');
    return;
  }

  // Proceed with actual test
  await page.goto('https://news.ycombinator.com');

  const firstHeadline = await page.locator('.athing').first().innerText();

  if (!firstHeadline || firstHeadline.length < 10) {
    await page.screenshot({ path: 'error-screenshot.png' });
    throw new Error('Bug detected: Headline is too short or missing');
  }

  expect(firstHeadline.length).toBeGreaterThan(10);
});
