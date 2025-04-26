import { test, expect } from '@playwright/test';
import { setupMockServer } from './utils/mockServer';

/**
 * E2E test for the dashboard functionality.
 * This test verifies:
 * 1. The dashboard page loads correctly with proper charts
 * 2. The sector allocation chart displays correctly
 * 3. The NAV over time chart renders properly
 * 4. The holdings table displays with sortable columns
 */
test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    // Setup MSW mock server
    await setupMockServer(page);
    
    // Navigate to the dashboard page
    await page.goto('/dashboard');
  });

  test('should render dashboard properly', async ({ page }) => {
    // Verify the page title
    await expect(page.locator('h1')).toContainText('Fund Dashboard');
    
    // Verify charts are rendered
    await expect(page.locator('text=Net Asset Value Over Time')).toBeVisible();
    await expect(page.locator('text=Sector Allocation')).toBeVisible();
    
    // Verify data table is displayed
    await expect(page.locator('text=Top Holdings')).toBeVisible();
    
    // Verify table headings
    await expect(page.locator('th >> text=Company')).toBeVisible();
    await expect(page.locator('th >> text=Sector')).toBeVisible();
    await expect(page.locator('th >> text=FMV')).toBeVisible();
    await expect(page.locator('th >> text=TVPI')).toBeVisible();
  });

  test('should sort holdings table correctly', async ({ page }) => {
    // Click on value column to sort by FMV
    await page.locator('th:has-text("FMV")').click();
    
    // Verify sorting indicator is visible
    await expect(page.locator('th:has-text("FMV") span')).toBeVisible();
    
    // Click again to reverse sort order
    await page.locator('th:has-text("FMV")').click();
    
    // Click on company name to sort alphabetically
    await page.locator('th:has-text("Company")').click();
    
    // Verify sorting indicator is visible on company column
    await expect(page.locator('th:has-text("Company") span')).toBeVisible();
  });
});