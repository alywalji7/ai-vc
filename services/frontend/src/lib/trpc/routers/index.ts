import { router } from '../server';
import { dashboardRouter } from './dashboard';
import { dealMemosRouter } from './deal-memos';
import { auditTrailRouter } from './audit-trail';

export const appRouter = router({
  dashboard: dashboardRouter,
  dealMemos: dealMemosRouter,
  auditTrail: auditTrailRouter,
});

// Export type definition of API
export type AppRouter = typeof appRouter;