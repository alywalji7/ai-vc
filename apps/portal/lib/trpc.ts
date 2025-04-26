import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import superjson from 'superjson';
import { AppRouter } from '../../../services/frontend/src/lib/trpc/api';

export const trpc = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'http://localhost:5000/api/trpc',
      transformer: superjson,
    }),
  ],
});