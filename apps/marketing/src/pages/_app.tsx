import React, { useEffect } from 'react';
import Layout from '../components/Layout';
import { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { initAnalytics, trackPageView } from '../lib/analytics';
import '../styles/globals.css';

const MyApp: React.FC<AppProps> = ({ Component, pageProps }) => {
  const router = useRouter();

  useEffect(() => {
    // Initialize analytics on mount
    initAnalytics();

    // Handle initial page load
    trackPageView(window.location.pathname);

    // Handle subsequent route changes
    const handleRouteChange = (url: string) => {
      trackPageView(url);
    };

    router.events.on('routeChangeComplete', handleRouteChange);

    // Clean up on unmount
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router]);

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
};

export default MyApp;