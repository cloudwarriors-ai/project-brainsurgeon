const { test, expect } = require('@playwright/test');

test('hello-world page loads correctly', async ({ page }) => {
  await page.goto('/');
  
  // Check that the page title is correct
  await expect(page).toHaveTitle('Hello World');
  
  // Check that the hello-world element exists and contains the expected text
  const helloWorldElement = page.locator('#hello-world');
  await expect(helloWorldElement).toBeVisible();
  await expect(helloWorldElement).toHaveText('Hello, World!');
  
  // Check that the paragraph text is present
  await expect(page.locator('p')).toHaveText('This is a simple hello-world application.');
});

test('hello-world element is present', async ({ page }) => {
  await page.goto('/');
  
  // Verify the hello-world element specifically
  const helloElement = page.locator('#hello-world');
  await expect(helloElement).toBeVisible();
  await expect(helloElement).toContainText('Hello, World!');
});