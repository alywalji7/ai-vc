import { router } from '../server';
import { dashboardRouter } from './dashboard';
import { dealMemosRouter } from './deal-memos';
import { auditTrailRouter } from './audit-trail';
import { startupRouter } from './startup';

export const appRouter = router({
  dashboard: dashboardRouter,
  dealMemos: dealMemosRouter,
  auditTrail: auditTrailRouter,
  startup: startupRouter,
});

// Export type definition of API
export type AppRouter = typeof appRouter;