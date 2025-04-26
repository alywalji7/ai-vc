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

// Define NAV history data shape
const NavHistoryPoint = z.object({
  date: z.string(),
  value: z.number(),
});

// Define top holding data shape
const TopHolding = z.object({
  id: z.string(),
  name: z.string(), 
  sector: z.string(),
  value: z.number(),
  costBasis: z.number(),
  moic: z.number(),
  percentOfNav: z.number(),
  changeMonth: z.number(),
  changeQuarter: z.number(),
  changeYear: z.number(),
});

// Define the fund metrics data shape
const FundMetrics = z.object({
  fundId: z.string(),
  metricsDate: z.string(),
  benchmarks: z.object({
    vc: z.number(),
    sp500: z.number(),
    nasdaq: z.number(),
  }),
  performance: z.object({
    oneMonth: z.number(),
    threeMonth: z.number(),
    ytd: z.number(),
    oneYear: z.number(),
    sinceInception: z.number(),
  }),
  topGainers: z.array(z.object({
    name: z.string(),
    gain: z.number(),
  })),
  topLosers: z.array(z.object({
    name: z.string(),
    loss: z.number(),
  })),
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

  // New endpoints for Fund Dashboard Deep-Dive
  getNavHistory: publicProcedure
    .input(
      z.object({
        fundId: z.string().optional(),
        timeframe: z.enum(['1m', '3m', '6m', '1y', '3y', 'all']).optional(),
      })
    )
    .query(async ({ input }) => {
      // In production, this would fetch from the telemetry service based on the fundId and timeframe
      // For now, we'll return hardcoded NAV history data
      const currentYear = new Date().getFullYear();
      
      // Generate monthly data points for the past year
      const dataPoints = [];
      for (let i = 0; i < 12; i++) {
        const date = new Date(currentYear, i, 1);
        const month = date.toLocaleString('default', { month: 'short' });
        const value = 25000000 + Math.floor(Math.random() * 20000000); // Random value between 25M and 45M
        dataPoints.push({
          date: `${month} ${currentYear}`,
          value: value,
        });
      }
      
      return dataPoints;
    }),

  getTopHoldings: publicProcedure
    .input(
      z.object({
        fundId: z.string().optional(),
        limit: z.number().default(10),
      })
    )
    .query(async ({ input }) => {
      // In production, this would fetch from the telemetry service based on the fundId
      // For now, we'll return hardcoded top holdings data
      const totalNav = 40000000;
      
      return [
        {
          id: 'acme-inc',
          name: 'Acme Inc',
          sector: 'AI Infrastructure',
          value: 15000000,
          costBasis: 5000000,
          moic: 3.0,
          percentOfNav: 37.5,
          changeMonth: 5.2,
          changeQuarter: 12.6,
          changeYear: 45.3,
        },
        {
          id: 'globex-llc',
          name: 'Globex LLC',
          sector: 'Enterprise SaaS',
          value: 3000000,
          costBasis: 1500000,
          moic: 2.0,
          percentOfNav: 7.5,
          changeMonth: 2.1,
          changeQuarter: 5.7,
          changeYear: 23.8,
        },
        {
          id: 'vector-ai',
          name: 'Vector AI',
          sector: 'LLM Applications',
          value: 1000000,
          costBasis: 2000000,
          moic: 0.5,
          percentOfNav: 2.5,
          changeMonth: -3.5,
          changeQuarter: -8.2,
          changeYear: -15.7,
        },
        {
          id: 'quantum-systems',
          name: 'Quantum Systems',
          sector: 'AI Infrastructure',
          value: 8000000,
          costBasis: 3000000,
          moic: 2.67,
          percentOfNav: 20.0,
          changeMonth: 4.2,
          changeQuarter: 9.6,
          changeYear: 35.1,
        },
        {
          id: 'neural-labs',
          name: 'Neural Labs',
          sector: 'Vertical AI',
          value: 6000000,
          costBasis: 2500000,
          moic: 2.4,
          percentOfNav: 15.0,
          changeMonth: 3.8,
          changeQuarter: 8.3,
          changeYear: 30.2,
        },
      ].slice(0, input.limit);
    }),

  getFundMetrics: publicProcedure
    .input(
      z.object({
        fundId: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      // In production, this would fetch from the telemetry service based on the fundId
      // For now, we'll return hardcoded fund metrics data
      return {
        fundId: input.fundId || 'fund-i',
        metricsDate: new Date().toISOString().split('T')[0],
        benchmarks: {
          vc: 0.15, // 15% annual return
          sp500: 0.10, // 10% annual return
          nasdaq: 0.12, // 12% annual return
        },
        performance: {
          oneMonth: 0.03, // 3% last month
          threeMonth: 0.08, // 8% last quarter
          ytd: 0.12, // 12% year-to-date
          oneYear: 0.22, // 22% last year
          sinceInception: 0.35, // 35% since inception
        },
        topGainers: [
          { name: 'Acme Inc', gain: 0.45 },
          { name: 'Quantum Systems', gain: 0.35 },
          { name: 'Neural Labs', gain: 0.30 },
        ],
        topLosers: [
          { name: 'Vector AI', gain: -0.15 },
          { name: 'DataSync', gain: -0.10 },
          { name: 'Nexus Networks', gain: -0.05 },
        ],
      };
    }),
});