import { startupRouter } from './routers/startup';
import { auditTrailRouter } from './routers/auditTrail';
import { dashboardRouter } from './routers/dashboard';
import { router } from './init';

// Create the app router that combines all routers
export const appRouter = router({
  startup: startupRouter,
  auditTrail: auditTrailRouter,
  dashboard: dashboardRouter,
  // add more routers here as needed
});

// Export type router type signature for client use
export type AppRouter = typeof appRouter;