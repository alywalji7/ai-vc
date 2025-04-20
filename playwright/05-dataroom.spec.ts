import { test, expect } from '@playwright/test';

/**
 * E2E test for the dataroom functionality.
 * This test verifies:
 * 1. The dataroom page for 'acme-inc' loads correctly
 * 2. The deck thumbnail is visible
 * 3. The KPI table has at least 3 rows
 */
test('dataroom page loads with expected content', async ({ page }) => {
  // Company ID for ACME Inc.
  const companyId = 'acme-inc';
  
  // Step 1: Navigate to the dataroom page for ACME Inc.
  await page.goto(`/dataroom/${companyId}`);
  
  // Wait for the page to load and verify company name is visible
  await expect(page.locator('h1:has-text("ACME Inc.")')).toBeVisible();
  
  // Step 2: Verify deck thumbnail is visible
  await expect(page.locator('.deck-thumbnail')).toBeVisible();
  
  // Step 3: Verify KPI table has at least 3 rows
  const kpiRows = page.locator('.kpi-table tbody tr');
  await expect(kpiRows).toHaveCount({ min: 3 });
  
  // Additional verification: Check if key metrics are present
  await expect(page.locator('.kpi-table')).toContainText('MRR');
  await expect(page.locator('.kpi-table')).toContainText('Customers');
  await expect(page.locator('.kpi-table')).toContainText('CAC');
  await expect(page.locator('.kpi-table')).toContainText('LTV');
});