import { useEffect } from 'react';
import { useRouter } from 'next/router';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { initAnalytics, trackPageView } from '../lib/analytics';
import '../styles/globals.css';

// Initialize analytics with environment variables
const analyticsConfig = {
  posthogToken: process.env.NEXT_PUBLIC_POSTHOG_TOKEN,
  gaTrackingId: process.env.NEXT_PUBLIC_GA_ID,
};

export default function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();

  // Initialize analytics on mount
  useEffect(() => {
    initAnalytics(analyticsConfig);
  }, []);

  // Track page views on route change
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      trackPageView(url);
    };

    // Track initial page view
    trackPageView(router.asPath);

    // Setup route change tracking
    router.events.on('routeChangeComplete', handleRouteChange);
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router]);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta charSet="utf-8" />
        <link rel="icon" href="/favicon.ico" />
        {/* Preload font */}
        <link
          rel="preload"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          as="style"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <Component {...pageProps} />
    </>
  );
}