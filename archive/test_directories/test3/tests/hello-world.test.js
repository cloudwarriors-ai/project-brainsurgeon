// BROKEN TEST FILE - Multiple syntax and logic errors
const { test, expect } = require('@playwright/test');

test.describe('Hello World Test3 BROKEN Application', () => {
  test('page loads correctly and displays hello world', async ({ page }) => {
    await page.goto('/');
    
    // WRONG: Looking for correct ID when HTML has wrong ID
    const helloWorldElement = page.locator('#hello-world');  // HTML has #broken-hello
    await expect(helloWorldElement).toBeVisible();
    await expect(helloWorldElement).toHaveText('Hello, World!');
  });

  test('broken test with invalid syntax', async ({ page }) => {
    await page.goto('/');
    
    // BROKEN: Invalid syntax - missing parentheses
    const element = page.locator('#nonexistent-element';
    await expect(element).toBeVisible();
  });

  test('test looking for missing elements', async ({ page }) => {
    await page.goto('/');
    
    // BROKEN: Looking for elements that don't exist
    await expect(page.locator('#missing-container')).toBeVisible();
    await expect(page.locator('#another-missing-element')).toContainText('Should not exist');
  });

  // BROKEN: Invalid test definition - missing async
  test('synchronous test that should be async', ({ page }) => {
    await page.goto('/');  // This will fail - await in non-async function
    const title = page.locator('title');
    await expect(title).toHaveText('Wrong Title');
  });
});