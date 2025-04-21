import { z } from 'zod';
import { publicProcedure, router } from '../server';

// Mock data for dashboard metrics
const getFundPerformanceData = () => ({
  navHistory: [
    { date: '2022-Q1', value: 100 },
    { date: '2022-Q2', value: 105 },
    { date: '2022-Q3', value: 112 },
    { date: '2022-Q4', value: 120 },
    { date: '2023-Q1', value: 125 },
    { date: '2023-Q2', value: 132 },
    { date: '2023-Q3', value: 140 },
    { date: '2023-Q4', value: 150 },
    { date: '2024-Q1', value: 160 },
    { date: '2024-Q2', value: 172 },
    { date: '2024-Q3', value: 185 },
    { date: '2024-Q4', value: 195 },
    { date: '2025-Q1', value: 210 },
  ],
  currentMetrics: {
    nav: 210000000, // $210M
    tvpi: 2.1,      // 2.1x
    dpi: 0.5,       // 0.5x
    irr: 28.6,      // 28.6%
    rvpi: 1.6,      // 1.6x
  },
  topPerformers: [
    { company: 'AI Insights', valuation: 80000000, multiplier: 4.0 },
    { company: 'Quantum Computing', valuation: 65000000, multiplier: 3.2 },
    { company: 'Sustainable Energy', valuation: 45000000, multiplier: 2.5 },
    { company: 'Biotech Innovations', valuation: 40000000, multiplier: 2.0 },
    { company: 'Cloud Security', valuation: 22000000, multiplier: 1.8 },
  ],
  sectorAllocation: [
    { sector: 'AI & ML', percentage: 35 },
    { sector: 'Enterprise SaaS', percentage: 25 },
    { sector: 'Fintech', percentage: 15 },
    { sector: 'Healthcare', percentage: 12 },
    { sector: 'CleanTech', percentage: 8 },
    { sector: 'Other', percentage: 5 },
  ]
});

export const dashboardRouter = router({
  getFundPerformance: publicProcedure.query(() => {
    return getFundPerformanceData();
  }),
  
  getPortfolioCompanies: publicProcedure.query(() => {
    // Return list of portfolio companies with basic metrics
    return [
      { id: 'highgrowth-saas-1', name: 'AI Insights', sector: 'AI & ML', stage: 'Series B', invested: 20000000, currentValue: 80000000, status: 'Active' },
      { id: 'quantum-computing-1', name: 'Quantum Computing', sector: 'Enterprise SaaS', stage: 'Series A', invested: 18000000, currentValue: 65000000, status: 'Active' },
      { id: 'sustainable-energy-1', name: 'Sustainable Energy', sector: 'CleanTech', stage: 'Series B', invested: 15000000, currentValue: 45000000, status: 'Active' },
      { id: 'biotech-innovations-1', name: 'Biotech Innovations', sector: 'Healthcare', stage: 'Series A', invested: 18000000, currentValue: 40000000, status: 'Active' },
      { id: 'lowrunway-hardware-1', name: 'Cloud Security', sector: 'Enterprise SaaS', stage: 'Seed', invested: 12000000, currentValue: 22000000, status: 'Follow-on Required' },
      { id: 'stable-fintech-1', name: 'Digital Banking', sector: 'Fintech', stage: 'Series C', invested: 25000000, currentValue: 40000000, status: 'Active' },
      { id: 'e-commerce-platform-1', name: 'E-Commerce Platform', sector: 'Enterprise SaaS', stage: 'Series A', invested: 10000000, currentValue: 14000000, status: 'Active' },
      { id: 'crypto-security-1', name: 'Crypto Security', sector: 'Fintech', stage: 'Seed', invested: 5000000, currentValue: 8000000, status: 'Active' },
    ];
  }),
  
  getCapitalCalls: publicProcedure.query(() => {
    // Return capital call history and upcoming calls
    return {
      history: [
        { id: 1, date: '2022-01-15', amount: 50000000, purpose: 'Initial capital call', status: 'Completed' },
        { id: 2, date: '2022-06-10', amount: 30000000, purpose: 'Follow-on investments', status: 'Completed' },
        { id: 3, date: '2023-03-22', amount: 40000000, purpose: 'New investments', status: 'Completed' },
        { id: 4, date: '2024-02-18', amount: 25000000, purpose: 'Follow-on investments', status: 'Completed' },
      ],
      upcoming: [
        { id: 5, date: '2025-05-15', amount: 20000000, purpose: 'Follow-on investments', status: 'Scheduled' },
      ]
    };
  }),
  
  getDistributions: publicProcedure.query(() => {
    // Return distribution history
    return [
      { id: 1, date: '2023-08-12', amount: 15000000, company: 'Early Exit Inc.', type: 'Exit', notes: 'Full acquisition by BigCorp' },
      { id: 2, date: '2024-04-05', amount: 8000000, company: 'Tech Solutions', type: 'Secondary', notes: 'Partial secondary sale' },
      { id: 3, date: '2024-11-20', amount: 22000000, company: 'Growth SaaS', type: 'Exit', notes: 'IPO proceeds - first distribution' },
      { id: 4, date: '2025-02-28', amount: 5000000, company: 'Growth SaaS', type: 'Exit', notes: 'IPO proceeds - second distribution' },
    ];
  }),
});