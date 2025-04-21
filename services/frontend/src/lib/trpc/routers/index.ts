import { router } from '../server';
import { dashboardRouter } from './dashboard';
import { dealMemosRouter } from './dealMemos';
import { auditTrailRouter } from './auditTrail';

export const appRouter = router({
  dashboard: dashboardRouter,
  dealMemos: dealMemosRouter,
  auditTrail: auditTrailRouter,
});

export type AppRouter = typeof appRouter;