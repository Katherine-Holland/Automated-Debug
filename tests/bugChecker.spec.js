const { test, expect } = require('@playwright/test');

test('Check Hacker News headlines and take screenshot if bug found', async ({ page }) => {
  await page.goto('https://news.ycombinator.com');

  const firstHeadline = await page.locator('.athing').first().innerText();

  // Simulated check for a "bug"
  if (!firstHeadline || firstHeadline.length < 500) {
    await page.screenshot({ path: 'error-screenshot.png' });
    throw new Error('Bug detected: Headline is too short or missing');
  }

  expect(firstHeadline.length).toBeGreaterThan(10);
});