import { Page } from '@playwright/test';

/**
 * Mock data for the fund metrics API
 */
const mockFundMetricsResponse = {
  navOverTime: {
    dates: [
      '2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', 
      '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01'
    ],
    nav: [10000000, 10500000, 11200000, 12000000, 13100000, 13400000, 14200000, 15000000]
  },
  sectorAllocation: [
    { name: 'Software', pct: 0.38 },
    { name: 'Fintech', pct: 0.22 },
    { name: 'Healthcare', pct: 0.15 },
    { name: 'AI/ML', pct: 0.12 },
    { name: 'Consumer', pct: 0.08 },
    { name: 'Other', pct: 0.05 }
  ],
  topHoldings: [
    { id: '1', name: 'TechCorp AI', value: 3200000, tvpi: 320, sector: 'AI/ML' },
    { id: '2', name: 'FinanceFlow', value: 2800000, tvpi: 280, sector: 'Fintech' },
    { id: '3', name: 'MedTech Solutions', value: 2400000, tvpi: 240, sector: 'Healthcare' },
    { id: '4', name: 'CloudWare', value: 1900000, tvpi: 190, sector: 'Software' },
    { id: '5', name: 'EcoShopper', value: 1500000, tvpi: 150, sector: 'Consumer' },
    { id: '6', name: 'DataFlow Systems', value: 1200000, tvpi: 120, sector: 'Software' },
    { id: '7', name: 'Quantum Computing', value: 900000, tvpi: 90, sector: 'AI/ML' },
    { id: '8', name: 'GreenEnergy', value: 600000, tvpi: 60, sector: 'Other' },
    { id: '9', name: 'MobileHealth', value: 300000, tvpi: 30, sector: 'Healthcare' },
    { id: '10', name: 'BlockPay', value: 200000, tvpi: 20, sector: 'Fintech' }
  ]
};

/**
 * Setup mock server for testing
 * This function injects MSW (Mock Service Worker) into the page and 
 * configures request handlers to intercept API calls
 */
export async function setupMockServer(page: Page): Promise<void> {
  // Register the MSW service worker in the Playwright page
  await page.addInitScript(() => {
    // @ts-ignore - since we're injecting this into the browser context
    window.mockServiceWorker = {
      handlers: {
        // Mock the fund metrics API endpoint
        '/api/trpc/fund.getMetrics': (req: any) => {
          return {
            result: {
              data: {
                json: mockFundMetricsResponse
              }
            }
          };
        },
        // Add health endpoint mock
        '/health': (req: any) => {
          return {
            status: "ok",
            timestamp: new Date().toISOString(),
            version: "0.1.0"
          };
        }
      }
    };
    
    // Intercept fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      let url: string;
      if (typeof input === 'string') {
        url = input;
      } else if (input instanceof URL) {
        url = input.toString();
      } else {
        // For Request objects
        url = input.url;
      }
      
      // @ts-ignore
      const handler = window.mockServiceWorker.handlers[url];
      if (handler) {
        // Return mocked response
        return new Response(JSON.stringify(handler()), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      // Pass through to original fetch for non-mocked endpoints
      return originalFetch(input, init);
    };
  });
}