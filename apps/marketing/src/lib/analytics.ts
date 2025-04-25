import posthog from 'posthog-js';
import ReactGA from 'react-ga4';

/**
 * Represents analytics configuration values.
 */
type AnalyticsConfig = {
  posthogToken?: string;
  gaTrackingId?: string;
};

/**
 * Whether analytics has been initialized.
 */
let isInitialized = false;

/**
 * Initialize analytics services.
 * @param config Analytics configuration including tokens.
 */
export function initAnalytics(config: AnalyticsConfig): void {
  if (isInitialized) {
    return;
  }

  // Initialize PostHog if token is provided
  if (config.posthogToken && typeof window !== 'undefined') {
    posthog.init(config.posthogToken, {
      api_host: 'https://app.posthog.com',
      autocapture: true,
      capture_pageview: false, // We'll handle this manually
      disable_session_recording: false,
      persistence: 'localStorage+cookie',
    });
    
    // Identify anonymous user with a random ID
    const anonymousId = localStorage.getItem('anonymous_id') || 
      `anon_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem('anonymous_id', anonymousId);
    posthog.identify(anonymousId);
  }

  // Initialize Google Analytics if tracking ID is provided
  if (config.gaTrackingId && typeof window !== 'undefined') {
    ReactGA.initialize(config.gaTrackingId);
  }

  isInitialized = true;
}

/**
 * Track page views in analytics platforms.
 * @param url The URL to track.
 */
export function trackPageView(url: string): void {
  if (!isInitialized || typeof window === 'undefined') {
    return;
  }

  // Get page title and clean URL
  const title = document.title;
  const cleanUrl = url.split('?')[0]; // Remove query parameters

  // Track in PostHog
  if (typeof posthog !== 'undefined' && posthog.capture) {
    posthog.capture('$pageview', {
      url: cleanUrl,
      title,
      referrer: document.referrer,
    });
  }

  // Track in Google Analytics
  if (typeof ReactGA !== 'undefined' && ReactGA.send) {
    ReactGA.send({ hitType: 'pageview', page: cleanUrl, title });
  }

  // Log if in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Analytics] Page view: ${cleanUrl}`);
  }
}

/**
 * Track custom events in analytics platforms.
 * @param eventName Name of the event.
 * @param properties Additional properties for the event.
 */
export function trackEvent(eventName: string, properties?: Record<string, any>): void {
  if (!isInitialized || typeof window === 'undefined') {
    return;
  }

  // Track in PostHog
  if (typeof posthog !== 'undefined' && posthog.capture) {
    posthog.capture(eventName, properties);
  }

  // Track in Google Analytics
  if (typeof ReactGA !== 'undefined' && ReactGA.event) {
    ReactGA.event({
      category: properties?.category || 'User Interaction',
      action: eventName,
      label: properties?.label,
      value: properties?.value,
    });
  }

  // Log if in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Analytics] Event: ${eventName}`, properties);
  }
}

/**
 * Get UTM parameters from the current URL.
 */
export function getUtmParams(): Record<string, string> {
  if (typeof window === 'undefined') {
    return {};
  }

  const urlParams = new URLSearchParams(window.location.search);
  const utmParams: Record<string, string> = {};
  
  // Extract UTM parameters
  const utmKeys = [
    'utm_source', 
    'utm_medium', 
    'utm_campaign', 
    'utm_term', 
    'utm_content'
  ];
  
  utmKeys.forEach(key => {
    const value = urlParams.get(key);
    if (value) {
      utmParams[key] = value;
    }
  });

  return utmParams;
}

/**
 * Get marketing attribution data.
 */
export function getAttributionData(): Record<string, string> {
  if (typeof window === 'undefined') {
    return {};
  }

  return {
    referrer: document.referrer || '',
    first_page_visited: localStorage.getItem('first_page_visited') || window.location.pathname,
    ...getUtmParams(),
  };
}

/**
 * Set the first page visited if it hasn't been set yet.
 */
export function setFirstPageVisited(): void {
  if (typeof window === 'undefined') {
    return;
  }

  if (!localStorage.getItem('first_page_visited')) {
    localStorage.setItem('first_page_visited', window.location.pathname);
  }
}

/**
 * Track form submission event.
 * @param formName Name of the form.
 * @param formData Data submitted in the form.
 */
export function trackFormSubmission(formName: string, formData: Record<string, any>): void {
  trackEvent('form_submission', {
    form_name: formName,
    form_data: { ...formData },
    ...getAttributionData(),
  });
}

// Set first page visited when the module is imported on the client side
if (typeof window !== 'undefined') {
  setFirstPageVisited();
}