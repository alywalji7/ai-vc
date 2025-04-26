import { z } from 'zod';
import { publicProcedure, router } from '../init';

// Define the fund performance type
export type FundPerformance = {
  id: string;
  name: string;
  vintage: number;
  tvpi: number;
  irr: number;
  dpi: number;
  rvpi: number;
  netCashFlow: number;
  capitalCalled: number;
  capitalCommitted: number;
  valuationDate: string;
};

// Define all possible metrics for fund performance
export enum FundMetric {
  TVPI = 'tvpi',
  IRR = 'irr',
  DPI = 'dpi',
  RVPI = 'rvpi',
  NET_CASH_FLOW = 'netCashFlow',
  CAPITAL_CALLED = 'capitalCalled',
  CAPITAL_COMMITTED = 'capitalCommitted',
}

// Input schema for fund performance (optional parameters)
const getFundPerformanceSchema = z.object({
  fundId: z.string().optional(),
  vintage: z.number().optional(),
  metrics: z.array(z.nativeEnum(FundMetric)).optional(),
}).optional();

export const dashboardRouter = router({
  // Get fund performance metrics
  getFundPerformance: publicProcedure
    .input(getFundPerformanceSchema)
    .query(async ({ input }) => {
      try {
        // In production, this would fetch from a database or performance calculation service
        // For now, we'll create some sample fund performance data
        const sampleFunds: FundPerformance[] = [
          {
            id: 'fund-1',
            name: 'AI.VC Fund I',
            vintage: 2021,
            tvpi: 1.8,
            irr: 0.22,
            dpi: 0.3,
            rvpi: 1.5,
            netCashFlow: -15000000,
            capitalCalled: 75000000,
            capitalCommitted: 100000000,
            valuationDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString() // 30 days ago
          },
          {
            id: 'fund-2',
            name: 'AI.VC Opportunity Fund',
            vintage: 2022,
            tvpi: 1.3,
            irr: 0.15,
            dpi: 0.1,
            rvpi: 1.2,
            netCashFlow: -25000000,
            capitalCalled: 50000000,
            capitalCommitted: 75000000,
            valuationDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString() // 30 days ago
          },
          {
            id: 'fund-3',
            name: 'AI.VC Fund II',
            vintage: 2023,
            tvpi: 1.1,
            irr: 0.08,
            dpi: 0.0,
            rvpi: 1.1,
            netCashFlow: -30000000,
            capitalCalled: 30000000,
            capitalCommitted: 150000000,
            valuationDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString() // 30 days ago
          }
        ];

        // Apply filters if provided
        let filteredFunds = [...sampleFunds];
        
        if (input?.fundId) {
          filteredFunds = filteredFunds.filter(fund => fund.id === input.fundId);
        }
        
        if (input?.vintage) {
          filteredFunds = filteredFunds.filter(fund => fund.vintage === input.vintage);
        }
        
        // Return specific metrics if requested, otherwise return all
        if (input?.metrics && input.metrics.length > 0) {
          return filteredFunds.map(fund => {
            const filteredFund: Partial<FundPerformance> = {
              id: fund.id,
              name: fund.name,
              vintage: fund.vintage,
              valuationDate: fund.valuationDate
            };
            
            // Add only the requested metrics
            input.metrics.forEach(metric => {
              filteredFund[metric] = fund[metric];
            });
            
            return filteredFund;
          });
        }
        
        return filteredFunds;
      } catch (error) {
        console.error('Error fetching fund performance:', error);
        throw new Error('Failed to fetch fund performance data');
      }
    }),

  // Additional dashboard endpoints can be added here
  getPortfolioAllocation: publicProcedure
    .query(async () => {
      // This would normally fetch portfolio allocation data from a database
      return {
        sectors: [
          { name: 'AI & ML', allocation: 0.35 },
          { name: 'SaaS', allocation: 0.25 },
          { name: 'Fintech', allocation: 0.15 },
          { name: 'Healthcare', allocation: 0.15 },
          { name: 'Consumer', allocation: 0.10 }
        ],
        stages: [
          { name: 'Seed', allocation: 0.40 },
          { name: 'Series A', allocation: 0.30 },
          { name: 'Series B', allocation: 0.20 },
          { name: 'Series C+', allocation: 0.10 }
        ],
        geography: [
          { name: 'North America', allocation: 0.65 },
          { name: 'Europe', allocation: 0.20 },
          { name: 'Asia', allocation: 0.10 },
          { name: 'Rest of World', allocation: 0.05 }
        ]
      };
    })
});