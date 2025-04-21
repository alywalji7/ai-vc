import { z } from 'zod';
import { publicProcedure, router } from '../server';

// Define the fund performance data shape
const FundPerformance = z.object({
  id: z.string(),
  name: z.string(),
  vintage: z.number(),
  committed: z.number(),
  contributed: z.number(),
  remaining: z.number(),
  distributed: z.number(),
  nav: z.number(),
  tvpi: z.number(),
  dpi: z.number(),
  irr: z.number(),
});

// Define the company data shape
const PortfolioCompany = z.object({
  id: z.string(),
  name: z.string(),
  logo: z.string(),
  sector: z.string(),
  stage: z.string(),
  investment_date: z.string(),
  initial_investment: z.number(),
  current_valuation: z.number(),
  moic: z.number(),
  status: z.enum(['active', 'exited', 'written_off']),
});

export const dashboardRouter = router({
  getFundPerformance: publicProcedure
    .query(async () => {
      // In production, this would fetch from the telemetry service 
      // For now, we'll return hardcoded data 
      return {
        id: 'fund-i',
        name: 'AI.VC Fund I',
        vintage: 2024,
        committed: 100000000,
        contributed: 35000000,
        remaining: 65000000,
        distributed: 10000000,
        nav: 40000000,
        tvpi: 1.43,
        dpi: 0.29,
        irr: 0.22,
      };
    }),
    
  getPortfolioCompanies: publicProcedure
    .query(async () => {
      // In production, this would fetch from the telemetry service
      // For now, we'll return hardcoded portfolio companies
      return [
        {
          id: 'acme-inc',
          name: 'Acme Inc',
          logo: '/logos/acme.svg',
          sector: 'AI Infrastructure',
          stage: 'Series A',
          investment_date: '2024-01-15',
          initial_investment: 5000000,
          current_valuation: 15000000,
          moic: 3.0,
          status: 'active',
        },
        {
          id: 'globex-llc',
          name: 'Globex LLC',
          logo: '/logos/globex.svg',
          sector: 'Enterprise SaaS',
          stage: 'Seed',
          investment_date: '2024-02-20',
          initial_investment: 1500000,
          current_valuation: 3000000,
          moic: 2.0,
          status: 'active',
        },
        {
          id: 'vector-ai',
          name: 'Vector AI',
          logo: '/logos/vector.svg',
          sector: 'LLM Applications',
          stage: 'Seed',
          investment_date: '2024-03-10',
          initial_investment: 2000000,
          current_valuation: 1000000,
          moic: 0.5,
          status: 'active',
        },
      ];
    }),
    
  getCashflowData: publicProcedure
    .query(async () => {
      // In production, this would fetch from the telemetry service
      const currentYear = new Date().getFullYear();
      
      // Return quarterly cashflow data for charting
      return {
        quarters: [
          `Q1 ${currentYear - 1}`,
          `Q2 ${currentYear - 1}`,
          `Q3 ${currentYear - 1}`,
          `Q4 ${currentYear - 1}`,
          `Q1 ${currentYear}`,
          `Q2 ${currentYear}`,
        ],
        inflows: [0, 0, 0, 10000000, 5000000, 20000000],
        outflows: [0, 0, 0, -15000000, -10000000, -10000000],
        net: [0, 0, 0, -5000000, -5000000, 10000000],
      };
    }),
    
  getSectorAllocation: publicProcedure
    .query(async () => {
      // In production, this would calculate from the portfolio companies data
      return [
        { sector: 'AI Infrastructure', allocation: 30 },
        { sector: 'Enterprise SaaS', allocation: 25 },
        { sector: 'LLM Applications', allocation: 20 },
        { sector: 'Vertical AI', allocation: 15 },
        { sector: 'Other', allocation: 10 },
      ];
    }),
});