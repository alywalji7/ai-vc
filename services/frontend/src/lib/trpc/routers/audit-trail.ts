import { z } from 'zod';
import { publicProcedure, router } from '../server';

// Define the audit log entry shape
const AuditLogEntry = z.object({
  id: z.string(),
  timestamp: z.string(),
  event_type: z.string(),
  user_id: z.string().optional(),
  user_name: z.string().optional(),
  entity_id: z.string().optional(),
  entity_type: z.string().optional(),
  entity_name: z.string().optional(),
  action: z.string(),
  details: z.record(z.any()).optional(),
  compliance_status: z.enum(['compliant', 'warning', 'violation']).optional(),
  payload_hash: z.string().optional(),
});

export const auditTrailRouter = router({
  getAuditLogs: publicProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(50),
        offset: z.number().min(0).default(0),
        entity_id: z.string().optional(),
        entity_type: z.string().optional(),
        event_type: z.string().optional(),
        start_date: z.string().optional(),
        end_date: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      // In production, this would fetch from the compliance system's audit log API
      // For now, we return example data
      
      const logs = [
        {
          id: 'log-00001',
          timestamp: '2024-04-20T10:15:32Z',
          event_type: 'investment_decision',
          user_id: 'user-001',
          user_name: 'Partner A',
          entity_id: 'acme-inc',
          entity_type: 'company',
          entity_name: 'Acme Inc',
          action: 'approved_investment',
          details: {
            amount: 5000000,
            valuation: 50000000,
            ownership: '10%',
            stage: 'Series A'
          },
          compliance_status: 'compliant',
          payload_hash: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
        },
        {
          id: 'log-00002',
          timestamp: '2024-04-18T14:22:45Z',
          event_type: 'due_diligence',
          user_id: 'user-002',
          user_name: 'Associate B',
          entity_id: 'globex-llc',
          entity_type: 'company',
          entity_name: 'Globex LLC',
          action: 'completed_due_diligence',
          details: {
            modules_completed: ['financial', 'technical', 'legal', 'market'],
            findings_count: 3,
            recommendation: 'proceed'
          },
          compliance_status: 'compliant',
          payload_hash: '3d7c4e1a7903c393bc99b1af32abfa6dfc2d4b1fa3d677284addd200126d9069',
        },
        {
          id: 'log-00003',
          timestamp: '2024-04-15T09:05:12Z',
          event_type: 'sanctions_check',
          user_id: 'system',
          user_name: 'Compliance System',
          entity_id: 'founder-15',
          entity_type: 'person',
          entity_name: 'John Smith',
          action: 'performed_sanctions_check',
          details: {
            check_type: 'OFAC',
            result: 'no_match',
            confidence: 0.99
          },
          compliance_status: 'compliant',
          payload_hash: '9a1f78598a225851a125f56871a3c4cd977edf29b1ad1de0efd1010a6bf32840',
        },
        {
          id: 'log-00004',
          timestamp: '2024-04-10T16:45:33Z',
          event_type: 'admin_override',
          user_id: 'user-001',
          user_name: 'Partner A',
          entity_id: 'vector-ai',
          entity_type: 'company',
          entity_name: 'Vector AI',
          action: 'override_investment_limit',
          details: {
            original_limit: '5%',
            new_limit: '8%',
            reason: 'Strategic investment in core AI infrastructure'
          },
          compliance_status: 'warning',
          payload_hash: '1f3870be274f6c49b3e31a0c6728957f032d4b1fa3d677284addd200126d9069',
        },
        {
          id: 'log-00005',
          timestamp: '2024-04-05T11:30:22Z',
          event_type: 'accreditation_verification',
          user_id: 'system',
          user_name: 'Compliance System',
          entity_id: 'investor-22',
          entity_type: 'investor',
          entity_name: 'Acme Capital',
          action: 'verified_accreditation',
          details: {
            method: 'document_review',
            expiration: '2025-04-05',
            reviewer: 'Legal Team'
          },
          compliance_status: 'compliant',
          payload_hash: '8e35c2cd3bf6641bdb0e2050b76932cbb2e4b1fa3d677284addd200126d9069',
        },
      ];
      
      return {
        logs: logs.slice(input.offset, input.offset + input.limit),
        total: logs.length,
      };
    }),
    
  verifyLogIntegrity: publicProcedure
    .input(z.object({
      log_id: z.string(),
    }))
    .query(async ({ input }) => {
      // In production, this would recalculate the hash and compare it to the stored hash
      return {
        verified: true,
        original_hash: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
        calculated_hash: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
        timestamp: '2024-04-21T14:22:33Z',
      };
    }),
});