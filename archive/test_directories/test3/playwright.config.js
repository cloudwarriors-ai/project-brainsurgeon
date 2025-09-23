// BROKEN PLAYWRIGHT CONFIG - Missing require and syntax errors
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  // BROKEN: Invalid configuration
  invalidProperty: "this-will-cause-errors",
  baseURL: 'http://localhost:WRONG_PORT',  // Wrong port number as string
  
  // BROKEN: Missing comma and invalid syntax
  projects: [
    {
      name: 'chromium'
      use: { ...devices['Desktop Chrome'] }  // Missing comma
    }
  ]
  // Missing webServer configuration
  // Missing reporter configuration
}