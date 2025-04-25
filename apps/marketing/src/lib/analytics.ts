import posthog from 'posthog-js';
import ReactGA from 'react-ga4';

export const initAnalytics = () => {
  try {
    // Initialize PostHog
    if (process.env.NEXT_PUBLIC_POSTHOG_KEY) {
      posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
        api_host: 'https://app.posthog.com',
        loaded: (posthog) => {
          if (process.env.NODE_ENV === 'development') {
            // Don't track in development
            posthog.opt_out_capturing();
          }
        }
      });
    }

    // Initialize Google Analytics
    if (process.env.NEXT_PUBLIC_GA4_ID) {
      ReactGA.initialize(process.env.NEXT_PUBLIC_GA4_ID);
    }
  } catch (error) {
    // Log the error but don't crash the app
    console.error('Analytics initialization error:', error);
  }
};

export const trackPageView = (url: string) => {
  try {
    // Track in PostHog
    if (process.env.NEXT_PUBLIC_POSTHOG_KEY) {
      posthog.capture('$pageview', {
        url
      });
    }

    // Track in Google Analytics
    if (process.env.NEXT_PUBLIC_GA4_ID) {
      ReactGA.send({ hitType: 'pageview', page: url });
    }
  } catch (error) {
    console.error('Error tracking page view:', error);
  }
};

export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  try {
    // Track in PostHog
    if (process.env.NEXT_PUBLIC_POSTHOG_KEY) {
      posthog.capture(eventName, properties);
    }

    // Track in Google Analytics
    if (process.env.NEXT_PUBLIC_GA4_ID) {
      ReactGA.event({
        category: properties?.category || 'User Action',
        action: eventName,
        label: properties?.label,
        value: properties?.value
      });
    }

    // Send to Customer.io webhook (if applicable)
    if (process.env.NEXT_PUBLIC_CUSTOMER_IO_WEBHOOK && properties?.email) {
      fetch(process.env.NEXT_PUBLIC_CUSTOMER_IO_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event: eventName,
          email: properties.email,
          ...properties
        })
      }).catch(err => console.error('Error sending to Customer.io:', err));
    }
  } catch (error) {
    console.error('Error tracking event:', error);
  }
};

export const identifyUser = (userId: string, traits?: Record<string, any>) => {
  try {
    // Identify in PostHog
    if (process.env.NEXT_PUBLIC_POSTHOG_KEY) {
      posthog.identify(userId, traits);
    }

    // No direct equivalent in GA4, but we can set user properties
    if (process.env.NEXT_PUBLIC_GA4_ID && traits) {
      ReactGA.set({ userId, ...traits });
    }
  } catch (error) {
    console.error('Error identifying user:', error);
  }
};