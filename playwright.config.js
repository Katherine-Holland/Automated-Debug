module.exports = {
    use: {
      headless: true,
      screenshot: 'only-on-failure',
      video: 'retain-on-failure',
      trace: 'on-first-retry',
    },
    timeout: 30000,
    retries: 1,
  };