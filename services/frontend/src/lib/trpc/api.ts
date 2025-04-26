'use client';

import { httpBatchLink } from '@trpc/client';
import { createTRPCNext } from '@trpc/next';
import superjson from 'superjson';
import { startupRouter } from './routers/startup';

// Define the type of our routers
type AppRouter = {
  startup: typeof startupRouter,
};

// Create the TRPC client
export const api = createTRPCNext<AppRouter>({
  config() {
    return {
      transformer: superjson,
      links: [
        httpBatchLink({
          url: '/api/trpc',
        }),
      ],
    };
  },
});