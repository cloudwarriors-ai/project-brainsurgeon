const { test, expect } = require('@playwright/test');

test.describe('Hello World Test2 Application', () => {
  test('page loads correctly and displays hello world', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page title is correct
    await expect(page).toHaveTitle('Hello World - Test2');
    
    // Check that the hello-world element exists and contains the expected text
    const helloWorldElement = page.locator('#hello-world');
    await expect(helloWorldElement).toBeVisible();
    await expect(helloWorldElement).toHaveText('Hello, World!');
  });

  test('description text is present and correct', async ({ page }) => {
    await page.goto('/');
    
    // Check that the description paragraph is present
    const description = page.locator('#description');
    await expect(description).toBeVisible();
    await expect(description).toContainText('Test2 - Enhanced hello-world application');
  });

  test('timestamp is displayed', async ({ page }) => {
    await page.goto('/');
    
    // Check that timestamp element is present
    const timestamp = page.locator('#timestamp');
    await expect(timestamp).toBeVisible();
    await expect(timestamp).toContainText('Built:');
    
    // Check that build time is populated
    const buildTime = page.locator('#build-time');
    await expect(buildTime).not.toBeEmpty();
  });

  test('styling is applied correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check that container has proper styling
    const container = page.locator('.container');
    await expect(container).toBeVisible();
    
    // Verify the gradient background is applied to body
    const bodyStyles = await page.evaluate(() => {
      const body = document.querySelector('body');
      return window.getComputedStyle(body).background;
    });
    
    expect(bodyStyles).toContain('linear-gradient');
  });

  test('hello-world element specifically exists', async ({ page }) => {
    await page.goto('/');
    
    // Specific test for the hello-world element as requested
    const helloElement = page.locator('#hello-world');
    await expect(helloElement).toBeVisible();
    await expect(helloElement).toContainText('Hello, World!');
    
    // Verify it's an h1 element
    await expect(helloElement).toHaveAttribute('id', 'hello-world');
  });
});