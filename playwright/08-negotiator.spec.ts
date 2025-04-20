import { test, expect } from '@playwright/test';

/**
 * E2E test for the term sheet negotiator functionality.
 * This test verifies:
 * 1. The negotiation chat page renders correctly
 * 2. Normal counter-offers (within 1σ) get a bot reply
 * 3. Extreme counter-offers (5x valuation) trigger the human override banner
 */
test('term sheet negotiator functionality', async ({ page }) => {
  // Deal ID for ACME Inc.
  const dealId = 'deal-acme-001';
  
  // Step 1: Navigate to the term sheet negotiation page
  await page.goto(`/term-sheet/chat/${dealId}`);
  
  // Wait for the page to load and verify elements are visible
  await expect(page.locator('h1:has-text("Term Sheet Negotiation")')).toBeVisible();
  await expect(page.locator('.chat-container')).toBeVisible();
  await expect(page.locator('.message-input')).toBeVisible();
  
  // Verify original terms are displayed correctly
  await expect(page.locator('.term-card:has-text("Valuation Cap")')).toBeVisible();
  await expect(page.locator('.term-card:has-text("Investment Amount")')).toBeVisible();
  await expect(page.locator('.term-card:has-text("Discount Rate")')).toBeVisible();
  
  // Step 2: Send a normal counter-offer (within 1σ variation)
  const normalCounterOffer = "I'd like to propose a valuation cap of $33M instead of $30M, which is a 10% increase.";
  
  await page.fill('.message-input', normalCounterOffer);
  await page.click('button:has-text("Send")');
  
  // Wait for the sent message to appear in the chat
  await expect(page.locator('.user-message:has-text("valuation cap of $33M")')).toBeVisible();
  
  // Wait for the bot's response (should appear within reasonable time)
  await expect(page.locator('.bot-message')).toBeVisible({ timeout: 10000 });
  
  // Verify no human override banner appears for normal counter-offer
  const humanOverrideBanner = page.locator('#human-override');
  await expect(humanOverrideBanner).not.toBeVisible();
  
  // Step 3: Send an extreme counter-offer (5x valuation)
  const extremeCounterOffer = "We'd like to increase the valuation cap to $150M, which is 5x the current valuation of $30M.";
  
  await page.fill('.message-input', extremeCounterOffer);
  await page.click('button:has-text("Send")');
  
  // Wait for the sent message to appear in the chat
  await expect(page.locator('.user-message:has-text("$150M")')).toBeVisible();
  
  // Wait for the human override banner to appear (should appear after extreme counter-offer)
  await expect(page.locator('#human-override')).toBeVisible({ timeout: 10000 });
  
  // Verify the human override banner contains the expected text
  await expect(page.locator('#human-override')).toContainText('Escalated to human review');
});