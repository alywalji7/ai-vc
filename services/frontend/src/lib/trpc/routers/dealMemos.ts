import { z } from 'zod';
import { publicProcedure, router } from '../server';

export const dealMemosRouter = router({
  // Get a list of all deal memos 
  getDealMemos: publicProcedure.query(() => {
    return [
      { 
        id: 1, 
        company: 'AI Insights', 
        date: '2022-03-15', 
        stage: 'Series B', 
        status: 'Approved',
        lead: 'Partner A',
        dealSize: 20000000,
        valuation: 100000000,
        ownership: 20,
        sector: 'AI & ML'
      },
      {
        id: 2,
        company: 'Quantum Computing',
        date: '2022-07-22',
        stage: 'Series A',
        status: 'Approved',
        lead: 'Partner B',
        dealSize: 18000000,
        valuation: 80000000,
        ownership: 22.5,
        sector: 'Enterprise SaaS'
      },
      {
        id: 3,
        company: 'Sustainable Energy',
        date: '2023-01-10',
        stage: 'Series B',
        status: 'Approved',
        lead: 'Partner A',
        dealSize: 15000000,
        valuation: 75000000,
        ownership: 20,
        sector: 'CleanTech'
      },
      {
        id: 4,
        company: 'Biotech Innovations',
        date: '2023-05-05',
        stage: 'Series A',
        status: 'Approved',
        lead: 'Partner C',
        dealSize: 18000000,
        valuation: 72000000,
        ownership: 25,
        sector: 'Healthcare'
      },
      {
        id: 5,
        company: 'Cloud Security',
        date: '2023-09-18',
        stage: 'Seed',
        status: 'Approved',
        lead: 'Partner B',
        dealSize: 12000000,
        valuation: 40000000,
        ownership: 30,
        sector: 'Enterprise SaaS'
      },
      {
        id: 6,
        company: 'Digital Banking',
        date: '2024-02-28',
        stage: 'Series C',
        status: 'Approved',
        lead: 'Partner A',
        dealSize: 25000000,
        valuation: 200000000,
        ownership: 12.5,
        sector: 'Fintech'
      },
      {
        id: 7,
        company: 'E-Commerce Platform',
        date: '2024-06-12',
        stage: 'Series A',
        status: 'Approved',
        lead: 'Partner C',
        dealSize: 10000000,
        valuation: 50000000,
        ownership: 20,
        sector: 'Enterprise SaaS'
      },
      {
        id: 8,
        company: 'Crypto Security',
        date: '2024-11-05',
        stage: 'Seed',
        status: 'Approved',
        lead: 'Partner B',
        dealSize: 5000000,
        valuation: 20000000,
        ownership: 25,
        sector: 'Fintech'
      }
    ];
  }),
  
  // Get a specific deal memo by ID
  getDealMemo: publicProcedure
    .input(z.object({ id: z.number() }))
    .query(({ input }) => {
      const memos = {
        1: {
          id: 1,
          company: 'AI Insights',
          date: '2022-03-15',
          stage: 'Series B',
          status: 'Approved',
          lead: 'Partner A',
          dealSize: 20000000,
          valuation: 100000000,
          ownership: 20,
          sector: 'AI & ML',
          content: {
            summary: 'AI Insights provides machine learning models for enterprise data analysis.',
            team: 'Strong technical team with prior exits. CEO previously founded and sold a data analytics company.',
            market: 'AI/ML market growing at 35% CAGR, expected to reach $500B by 2028.',
            product: 'SaaS platform with proprietary ML models for predictive analytics.',
            businessModel: 'Annual subscriptions with 92% gross margin. Average contract value of $180K.',
            competition: 'Main competitors include DataRobot and H2O.ai.',
            financials: {
              currentARR: '18M',
              burnRate: '800K/month',
              runway: '22 months',
              growthRate: '140% YoY',
            },
            dealTerms: 'Leading $20M Series B round at $100M valuation. 20% ownership stake.',
            risks: 'Competitive market with rapid innovation cycles. Talent acquisition is challenging.',
            thesisPoints: [
              'Proprietary AI models show 40% better prediction accuracy than competitors',
              'Strong enterprise customer base with 95% retention rate',
              'Technical moat with 8 pending patents',
              'Experienced team with domain expertise and prior exits'
            ],
            icVote: 'Unanimous approval with 5/5 vote',
          }
        },
        2: {
          id: 2,
          company: 'Quantum Computing',
          date: '2022-07-22',
          stage: 'Series A',
          status: 'Approved',
          lead: 'Partner B',
          dealSize: 18000000,
          valuation: 80000000,
          ownership: 22.5,
          sector: 'Enterprise SaaS',
          content: {
            summary: 'Quantum Computing develops enterprise software that simulates quantum algorithms on classical hardware.',
            team: 'PhD founders from MIT with publications in quantum computing.',
            market: 'Quantum computing software market projected to grow to $850M by 2030.',
            product: 'Quantum simulation platform for enterprise R&D departments.',
            businessModel: 'Enterprise licenses starting at $250K annually.',
            competition: 'IBM Quantum and D-Wave offer hardware solutions but limited software.',
            financials: {
              currentARR: '6M',
              burnRate: '600K/month',
              runway: '18 months post-funding',
              growthRate: '200% YoY',
            },
            dealTerms: 'Investing $18M in Series A at $80M valuation. 22.5% ownership.',
            risks: 'Technology is still early. Hardware advances may outpace software needs.',
            thesisPoints: [
              'First-to-market with enterprise-grade quantum simulation software',
              'Partnerships with 3 of 5 leading quantum hardware manufacturers',
              'Strong IP portfolio with 12 patents',
              'Scalable business model with high margins'
            ],
            icVote: 'Approved with 4/5 vote (one partner abstained)',
          }
        },
      };
      return memos[input.id as keyof typeof memos] || null;
    })
});