import { initTRPC } from '@trpc/server';
import superjson from 'superjson';

// Create a new instance of tRPC with type-safety
const t = initTRPC.create({
  transformer: superjson,
});

// Export the reusable router and procedure builders
export const router = t.router;
export const procedure = t.procedure;