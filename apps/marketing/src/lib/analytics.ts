import posthog from 'posthog-js';
import ReactGA from 'react-ga4';

interface AnalyticsConfig {
  posthogToken?: string;
  gaTrackingId?: string;
}

interface EventData {
  [key: string]: any;
}

/**
 * Initialize analytics with PostHog and Google Analytics
 */
export function initAnalytics(config: AnalyticsConfig): void {
  try {
    // Initialize PostHog if token is provided
    if (config.posthogToken) {
      posthog.init(config.posthogToken, {
        api_host: 'https://app.posthog.com',
        loaded: (posthog) => {
          if (process.env.NODE_ENV !== 'production') {
            // Disable capturing in development
            posthog.opt_out_capturing();
          }
        },
      });
      console.info('PostHog initialized');
    }

    // Initialize GA4 if tracking ID is provided
    if (config.gaTrackingId) {
      ReactGA.initialize(config.gaTrackingId);
      console.info('Google Analytics initialized');
    }
  } catch (error) {
    console.error('Failed to initialize analytics:', error);
  }
}

/**
 * Track page view
 */
export function trackPageView(path: string): void {
  try {
    // Track in PostHog
    posthog.capture('$pageview', {
      path,
      url: typeof window !== 'undefined' ? window.location.href : null,
      referrer: typeof document !== 'undefined' ? document.referrer : null,
    });

    // Track in GA
    ReactGA.send({ hitType: 'pageview', page: path });
  } catch (error) {
    console.error('Failed to track page view:', error);
  }
}

/**
 * Track custom event
 */
export function trackEvent(eventName: string, eventData?: EventData): void {
  try {
    // Track in PostHog
    posthog.capture(eventName, eventData);

    // Track in GA
    ReactGA.event({
      category: eventData?.category || 'User Action',
      action: eventName,
      label: eventData?.label,
      value: eventData?.value,
    });
  } catch (error) {
    console.error(`Failed to track event ${eventName}:`, error);
  }
}

/**
 * Identify user
 */
export function identifyUser(userId: string, userTraits?: { [key: string]: any }): void {
  try {
    // Identify in PostHog
    posthog.identify(userId, userTraits);

    // GA4 doesn't have a direct equivalent to identify
    // but we can set user properties
    if (userTraits) {
      ReactGA.set({
        userId,
        ...userTraits,
      });
    }
  } catch (error) {
    console.error('Failed to identify user:', error);
  }
}

/**
 * Reset (anonymize) current user
 */
export function resetUser(): void {
  try {
    // Reset in PostHog
    posthog.reset();

    // Reset in GA - set to anonymous
    ReactGA.set({ userId: undefined });
  } catch (error) {
    console.error('Failed to reset user:', error);
  }
}