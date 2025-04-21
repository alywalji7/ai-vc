import { z } from 'zod';
import { publicProcedure, router } from '../server';

export const auditTrailRouter = router({
  // Get audit trail entries with optional filtering
  getAuditTrail: publicProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(50),
        offset: z.number().min(0).default(0),
        eventType: z.string().optional(),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
        entityId: z.string().optional(),
      }).optional()
    )
    .query(({ input }) => {
      // Simulated audit log entries
      const auditLogs = [
        {
          id: 1,
          timestamp: '2025-04-21T10:15:32Z',
          eventType: 'investment_decision',
          user: 'Partner A',
          entity: 'Crypto Security',
          entityId: 'crypto-security-1',
          action: 'approved_investment',
          details: 'Approved $5M Seed investment at $20M valuation (25% ownership)',
          ipAddress: '192.168.1.105',
          hashData: 'c7a8e913f7e9d2e0b5a3958b6eb63264a2f19da782fcb7e898d8e5d45ad2868f',
        },
        {
          id: 2,
          timestamp: '2025-04-20T14:22:45Z',
          eventType: 'ic_meeting',
          user: 'System',
          entity: 'Investment Committee',
          entityId: 'ic-meeting-45',
          action: 'meeting_recorded',
          details: 'IC Meeting #45: Reviewed 3 potential investments, approved 2, rejected 1',
          ipAddress: '192.168.1.100',
          hashData: '4b79f9a5b7e4c2d0e8f6a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2',
        },
        {
          id: 3,
          timestamp: '2025-04-18T09:30:12Z',
          eventType: 'follow_on_decision',
          user: 'Partner B',
          entity: 'Cloud Security',
          entityId: 'lowrunway-hardware-1',
          action: 'approved_follow_on',
          details: 'Approved $1.82M follow-on investment to extend runway by 14 months',
          ipAddress: '192.168.1.110',
          hashData: '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8',
        },
        {
          id: 4,
          timestamp: '2025-04-15T16:45:22Z',
          eventType: 'document_access',
          user: 'Limited Partner C',
          entity: 'Quarterly Report Q1 2025',
          entityId: 'doc-q1-2025-report',
          action: 'document_downloaded',
          details: 'Downloaded Q1 2025 quarterly investor report',
          ipAddress: '203.0.113.42',
          hashData: '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
        },
        {
          id: 5,
          timestamp: '2025-04-10T11:20:33Z',
          eventType: 'capital_call',
          user: 'Partner A',
          entity: 'Fund Administration',
          entityId: 'capital-call-12',
          action: 'capital_call_issued',
          details: 'Issued $20M capital call for follow-on investments, due May 15, 2025',
          ipAddress: '192.168.1.105',
          hashData: 'f1e2d3c4b5a6987654321f1e2d3c4b5a6987654321f1e2d3c4b5a6987654321',
        },
        {
          id: 6,
          timestamp: '2025-04-08T14:10:05Z',
          eventType: 'valuation_update',
          user: 'Partner C',
          entity: 'Portfolio Valuation',
          entityId: 'valuation-q1-2025',
          action: 'valuation_approved',
          details: 'Approved Q1 2025 portfolio valuation update: NAV $210M, TVPI 2.1x',
          ipAddress: '192.168.1.115',
          hashData: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
        },
        {
          id: 7,
          timestamp: '2025-04-03T09:55:43Z',
          eventType: 'distribution',
          user: 'Partner A',
          entity: 'Fund Administration',
          entityId: 'distribution-8',
          action: 'distribution_issued',
          details: 'Issued $5M distribution from Growth SaaS IPO proceeds to LPs',
          ipAddress: '192.168.1.105',
          hashData: '7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6',
        },
        {
          id: 8,
          timestamp: '2025-04-01T16:32:18Z',
          eventType: 'term_sheet',
          user: 'Partner B',
          entity: 'Quantum Computing',
          entityId: 'quantum-computing-1',
          action: 'term_sheet_modified',
          details: 'Modified term sheet for follow-on investment - adjusted board seat provisions',
          ipAddress: '192.168.1.110',
          hashData: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3',
        },
        {
          id: 9,
          timestamp: '2025-03-28T10:45:22Z',
          eventType: 'due_diligence',
          user: 'Associate D',
          entity: 'New Prospect Inc.',
          entityId: 'due-diligence-32',
          action: 'due_diligence_completed',
          details: 'Completed technical due diligence for potential Series A investment',
          ipAddress: '192.168.1.120',
          hashData: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4',
        },
        {
          id: 10,
          timestamp: '2025-03-25T13:20:10Z',
          eventType: 'compliance_check',
          user: 'Compliance Officer',
          entity: 'New Prospect Inc.',
          entityId: 'compliance-check-45',
          action: 'kyc_aml_completed',
          details: 'Completed KYC/AML checks for potential investment target',
          ipAddress: '192.168.1.125',
          hashData: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5',
        },
      ];
      
      // Return the logs with total count
      return {
        logs: auditLogs,
        total: auditLogs.length
      };
    }),
  
  // Get audit entry details by ID
  getAuditEntryById: publicProcedure
    .input(z.object({ id: z.number() }))
    .query(({ input }) => {
      const auditLogs = {
        1: {
          id: 1,
          timestamp: '2025-04-21T10:15:32Z',
          eventType: 'investment_decision',
          user: 'Partner A',
          entity: 'Crypto Security',
          entityId: 'crypto-security-1',
          action: 'approved_investment',
          details: 'Approved $5M Seed investment at $20M valuation (25% ownership)',
          ipAddress: '192.168.1.105',
          hashData: 'c7a8e913f7e9d2e0b5a3958b6eb63264a2f19da782fcb7e898d8e5d45ad2868f',
          additionalData: {
            investmentCommitteeVote: '5/5 approval',
            investmentThesis: 'Strong team with prior security expertise, addressing growing market need',
            approvalProcess: 'Standard approval process followed, all documentation verified',
            legalDocuments: [
              'Term Sheet v1.2',
              'Stock Purchase Agreement',
              'Voting Agreement',
              'Right of First Refusal Agreement'
            ],
            riskAssessment: 'Medium risk profile, mitigated by experienced team and strong market position',
            expectedReturnMultiple: '4-5x',
            expectedExitTimeframe: '5-7 years'
          }
        }
      };
      
      return auditLogs[input.id as keyof typeof auditLogs] || null;
    }),
  
  // Get audit summary statistics
  getAuditStats: publicProcedure.query(() => {
    return {
      eventTypeBreakdown: [
        { type: 'investment_decision', count: 15 },
        { type: 'follow_on_decision', count: 8 },
        { type: 'document_access', count: 47 },
        { type: 'capital_call', count: 5 },
        { type: 'distribution', count: 4 },
        { type: 'valuation_update', count: 12 },
        { type: 'term_sheet', count: 18 },
        { type: 'due_diligence', count: 25 },
        { type: 'compliance_check', count: 32 },
        { type: 'ic_meeting', count: 24 },
      ],
      activityTimeline: [
        { month: '2024-05', count: 20 },
        { month: '2024-06', count: 15 },
        { month: '2024-07', count: 22 },
        { month: '2024-08', count: 18 },
        { month: '2024-09', count: 24 },
        { month: '2024-10', count: 19 },
        { month: '2024-11', count: 15 },
        { month: '2024-12', count: 12 },
        { month: '2025-01', count: 25 },
        { month: '2025-02', count: 28 },
        { month: '2025-03', count: 32 },
        { month: '2025-04', count: 22 },
      ],
      topUsers: [
        { user: 'Partner A', count: 45 },
        { user: 'Partner B', count: 38 },
        { user: 'Partner C', count: 32 },
        { user: 'Associate D', count: 28 },
        { user: 'Compliance Officer', count: 35 },
      ]
    };
  }),
});