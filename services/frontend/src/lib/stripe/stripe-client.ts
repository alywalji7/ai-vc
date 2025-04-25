/**
 * Stripe client utilities and constants
 */

export const subscriptionTiers = {
  STARTER: 'starter',
  PRO: 'pro',
  ENTERPRISE: 'enterprise',
} as const;

export const tierDetails = {
  [subscriptionTiers.STARTER]: {
    name: 'Starter',
    price: 500,
    features: [
      'Deal sourcing with AI',
      'Knowledge graph access',
      'Basic analytics',
      '5 companies',
      'Email support',
    ],
  },
  [subscriptionTiers.PRO]: {
    name: 'Pro',
    price: 1000,
    features: [
      'Everything in Starter',
      'Advanced analytics',
      'Investment Committee simulator',
      '25 companies',
      'Priority support',
      'API access',
    ],
  },
  [subscriptionTiers.ENTERPRISE]: {
    name: 'Enterprise',
    price: 2000,
    features: [
      'Everything in Pro',
      'Unlimited companies',
      'Custom integrations',
      'Dedicated support',
      'White-glove onboarding',
      'SSO & team management',
    ],
  },
};

/**
 * Format price in USD with appropriate notation
 */
export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}