const { test, expect } = require('@playwright/test');

test.describe('Hello World Test4 Application', () => {
  test('page loads correctly and displays hello world', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page title is correct
    await expect(page).toHaveTitle('Hello World - Test4');
    
    // ISSUE: Looking for #hello-world but HTML has #greeting
    const helloWorldElement = page.locator('#hello-world');
    await expect(helloWorldElement).toBeVisible();
    await expect(helloWorldElement).toHaveText('Hello, World!');
  });

  test('description text is present', async ({ page }) => {
    await page.goto('/');
    
    // Check that the description paragraph is present (be more specific)
    await expect(page.locator('p').first()).toContainText('Test4');
  });

  // ISSUE: Test expects timestamp element that doesn't exist in HTML
  test('timestamp is displayed', async ({ page }) => {
    await page.goto('/');
    
    const timestamp = page.locator('#timestamp');
    await expect(timestamp).toBeVisible();
  });
});