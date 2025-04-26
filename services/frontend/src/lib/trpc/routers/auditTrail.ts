import { z } from 'zod';
import { publicProcedure, router } from '../init';

// Define the schema for audit log queries
const getAuditLogsSchema = z.object({
  limit: z.number().min(1).max(100).default(25),
  offset: z.number().min(0).default(0),
  userId: z.string().optional(),
  actionType: z.string().optional(),
  startDate: z.string().optional(), // ISO string format
  endDate: z.string().optional(),   // ISO string format
});

// Define the audit log entry type
export type AuditLogEntry = {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  entityType: string;
  entityId: string;
  details: Record<string, any>;
};

export const auditTrailRouter = router({
  getAuditLogs: publicProcedure
    .input(getAuditLogsSchema)
    .query(async ({ input }) => {
      try {
        // In production, this would fetch from a database or audit service
        // For now, we'll create some sample audit logs
        const sampleAuditLogs: AuditLogEntry[] = [
          {
            id: '1',
            timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
            userId: 'user-123',
            userName: 'Jane Smith',
            action: 'VIEW',
            entityType: 'COMPANY',
            entityId: 'acme-inc',
            details: { ip: '192.168.1.1', userAgent: 'Mozilla/5.0' }
          },
          {
            id: '2',
            timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
            userId: 'user-456',
            userName: 'John Doe',
            action: 'EDIT',
            entityType: 'COMPANY',
            entityId: 'globex-llc',
            details: { fields: ['description', 'sector'], ip: '192.168.1.2' }
          },
          {
            id: '3',
            timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
            userId: 'user-789',
            userName: 'Alice Johnson',
            action: 'CREATE',
            entityType: 'DEAL',
            entityId: 'deal-123',
            details: { companyId: 'acme-inc', amount: 1000000, ip: '192.168.1.3' }
          }
        ];

        // Apply filters from input
        let filteredLogs = [...sampleAuditLogs];
        
        if (input.userId) {
          filteredLogs = filteredLogs.filter(log => log.userId === input.userId);
        }
        
        if (input.actionType) {
          filteredLogs = filteredLogs.filter(log => log.action === input.actionType);
        }
        
        if (input.startDate) {
          const startDate = new Date(input.startDate);
          filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= startDate);
        }
        
        if (input.endDate) {
          const endDate = new Date(input.endDate);
          filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) <= endDate);
        }
        
        // Sort by timestamp (newest first)
        filteredLogs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        
        // Apply pagination
        const paginatedLogs = filteredLogs.slice(input.offset, input.offset + input.limit);
        
        return {
          logs: paginatedLogs,
          total: filteredLogs.length,
          limit: input.limit,
          offset: input.offset
        };
      } catch (error) {
        console.error('Error fetching audit logs:', error);
        throw new Error('Failed to fetch audit logs');
      }
    }),
});