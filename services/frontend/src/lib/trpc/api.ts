import { createTRPCReact } from '@trpc/react-query';
import { startupRouter } from './routers/startup';

// Create the appRouter type with all of our router endpoints
export type AppRouter = typeof appRouter;

// Create a combined router with all of our router endpoints
export const appRouter = {
  startup: startupRouter,
};

// Create the tRPC React hooks
export const api = createTRPCReact<AppRouter>();