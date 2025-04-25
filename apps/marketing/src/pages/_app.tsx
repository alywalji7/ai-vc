import { useEffect } from 'react';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { initAnalytics, trackPageView } from '../lib/analytics';
import '../styles/globals.css';

// Analytics configuration
const ANALYTICS_CONFIG = {
  posthogToken: process.env.NEXT_PUBLIC_POSTHOG_TOKEN,
  gaTrackingId: process.env.NEXT_PUBLIC_GA_TRACKING_ID,
};

export default function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();

  // Initialize analytics
  useEffect(() => {
    initAnalytics(ANALYTICS_CONFIG);
  }, []);

  // Track page views on route change
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      trackPageView(url);
    };

    // Track initial page load
    trackPageView(router.asPath);

    // Track subsequent route changes
    router.events.on('routeChangeComplete', handleRouteChange);
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router.asPath, router.events]);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta charSet="utf-8" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5" />
        <meta name="msapplication-TileColor" content="#1f55f7" />
        <meta name="theme-color" content="#ffffff" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}