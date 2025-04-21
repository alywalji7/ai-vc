import { z } from 'zod';
import { publicProcedure, router } from '../server';

// Define the deal memo shape
const DealMemo = z.object({
  id: z.string(),
  company_id: z.string(),
  company_name: z.string(),
  memo_date: z.string(),
  stage: z.string(),
  investment_thesis: z.string(),
  market_analysis: z.string(),
  team_assessment: z.string(),
  product_analysis: z.string(),
  financial_overview: z.string(),
  valuation: z.number(),
  proposed_investment: z.number(),
  recommended_allocation: z.number(),
  decision: z.enum(['approved', 'rejected', 'pending']),
  decision_rationale: z.string().optional(),
  ic_members: z.array(z.string()),
  attachments: z.array(z.object({
    id: z.string(),
    name: z.string(),
    type: z.string(),
    url: z.string(),
  })).optional(),
});

export const dealMemosRouter = router({
  getAllDealMemos: publicProcedure
    .query(async () => {
      // In production, this would fetch from the backend API
      return [
        {
          id: 'memo-001',
          company_id: 'acme-inc',
          company_name: 'Acme Inc',
          memo_date: '2023-12-20',
          stage: 'Series A',
          decision: 'approved',
          valuation: 50000000,
          proposed_investment: 5000000,
        },
        {
          id: 'memo-002',
          company_id: 'globex-llc',
          company_name: 'Globex LLC',
          memo_date: '2024-01-15',
          stage: 'Seed',
          decision: 'approved',
          valuation: 15000000,
          proposed_investment: 1500000,
        },
        {
          id: 'memo-003',
          company_id: 'vector-ai',
          company_name: 'Vector AI',
          memo_date: '2024-02-28',
          stage: 'Seed',
          decision: 'approved',
          valuation: 20000000,
          proposed_investment: 2000000,
        },
        {
          id: 'memo-004',
          company_id: 'quantum-labs',
          company_name: 'Quantum Labs',
          memo_date: '2024-03-15',
          stage: 'Pre-seed',
          decision: 'rejected',
          valuation: 8000000,
          proposed_investment: 1000000,
        },
        {
          id: 'memo-005',
          company_id: 'neuralink-clone',
          company_name: 'Cortex Connect',
          memo_date: '2024-04-10',
          stage: 'Series B',
          decision: 'pending',
          valuation: 150000000,
          proposed_investment: 10000000,
        },
      ];
    }),
    
  getDealMemoById: publicProcedure
    .input(z.object({
      id: z.string(),
    }))
    .query(async ({ input }) => {
      // In production, this would fetch the specific memo from the backend
      // For now we'll return a hardcoded memo
      
      const memos: Record<string, any> = {
        'memo-001': {
          id: 'memo-001',
          company_id: 'acme-inc',
          company_name: 'Acme Inc',
          memo_date: '2023-12-20',
          stage: 'Series A',
          investment_thesis: 'Acme is positioned to be a key infrastructure provider for AI model deployment with their serverless inference platform. Their technology significantly reduces the cost and complexity of deploying large language models in production.',
          market_analysis: 'The AI infrastructure market is growing at 35% CAGR and expected to reach $250B by 2030. Acme addresses the critical bottleneck of inference costs which currently represent 80-90% of total AI deployment expenses.',
          team_assessment: 'Founded by ex-Google TPU team members with deep expertise in ML systems and optimization. CEO previously scaled Tensor Systems to $50M ARR before acquisition.',
          product_analysis: 'Their dynamic batching and model quantization technology shows 65% cost reduction compared to current market leaders. Early customer feedback indicates strong retention and rapid expansion.',
          financial_overview: 'Current ARR of $2.4M with 25% MoM growth. Burn rate of $400K/month gives 18 months of runway post-investment.',
          valuation: 50000000,
          proposed_investment: 5000000,
          recommended_allocation: 5,
          decision: 'approved',
          decision_rationale: 'Strong technical team addressing a growing market with proven technology and early customer traction. Unanimous IC approval.',
          ic_members: ['Partner A', 'Partner B', 'Partner C', 'Partner D'],
          attachments: [
            { id: 'att-001', name: 'Technical Due Diligence Report', type: 'pdf', url: '/memos/acme-tech-dd.pdf' },
            { id: 'att-002', name: 'Financial Model', type: 'xlsx', url: '/memos/acme-financial-model.xlsx' },
            { id: 'att-003', name: 'Customer References', type: 'pdf', url: '/memos/acme-customer-refs.pdf' },
          ],
        },
        // More memos would be defined here in production
      };
      
      return memos[input.id] || null;
    }),
});