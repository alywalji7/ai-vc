'use client';

import { useState } from 'react';
import { Check, Shield, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { subscriptionTiers, tierDetails, formatPrice } from '@/lib/stripe/stripe-client';

export default function PricingPage() {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});
  const { toast } = useToast();

  const handleSubscribe = async (planId: string) => {
    setIsLoading((prev) => ({ ...prev, [planId]: true }));

    try {
      // Call the API to create a checkout session
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ planId }),
      });

      const data = await response.json();

      if (response.ok && data.url) {
        // Redirect to the Stripe checkout page
        window.location.href = data.url;
      } else {
        throw new Error(data.error || 'Failed to create checkout session');
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'An error occurred. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading((prev) => ({ ...prev, [planId]: false }));
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Simple, Transparent Pricing</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Choose the plan that suits your investment strategy. All plans include access to our AI-powered deal sourcing platform.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {/* Starter Plan */}
        <Card className="flex flex-col border-2 border-muted">
          <CardHeader>
            <div className="flex items-center justify-center mb-2">
              <Shield className="h-8 w-8 text-blue-500" />
            </div>
            <CardTitle className="text-2xl text-center">{tierDetails[subscriptionTiers.STARTER].name}</CardTitle>
            <CardDescription className="text-center">For individual angel investors</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <div className="text-center mb-6">
              <span className="text-4xl font-bold">{formatPrice(tierDetails[subscriptionTiers.STARTER].price)}</span>
              <span className="text-muted-foreground">/month</span>
            </div>
            <ul className="space-y-2">
              {tierDetails[subscriptionTiers.STARTER].features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => handleSubscribe(subscriptionTiers.STARTER)}
              isLoading={isLoading[subscriptionTiers.STARTER]}
              className="w-full"
            >
              Subscribe
            </Button>
          </CardFooter>
        </Card>

        {/* Pro Plan */}
        <Card className="flex flex-col border-2 border-primary relative">
          <div className="absolute top-0 right-0 -translate-y-1/2 px-3 py-1 bg-primary text-primary-foreground rounded-full text-sm font-medium">
            Popular
          </div>
          <CardHeader>
            <div className="flex items-center justify-center mb-2">
              <Zap className="h-8 w-8 text-yellow-500" />
            </div>
            <CardTitle className="text-2xl text-center">{tierDetails[subscriptionTiers.PRO].name}</CardTitle>
            <CardDescription className="text-center">For professional investors</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <div className="text-center mb-6">
              <span className="text-4xl font-bold">{formatPrice(tierDetails[subscriptionTiers.PRO].price)}</span>
              <span className="text-muted-foreground">/month</span>
            </div>
            <ul className="space-y-2">
              {tierDetails[subscriptionTiers.PRO].features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => handleSubscribe(subscriptionTiers.PRO)}
              isLoading={isLoading[subscriptionTiers.PRO]}
              className="w-full"
              variant="default"
            >
              Subscribe
            </Button>
          </CardFooter>
        </Card>

        {/* Enterprise Plan */}
        <Card className="flex flex-col border-2 border-muted">
          <CardHeader>
            <div className="flex items-center justify-center mb-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-8 w-8 text-purple-500"
              >
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
                <path d="M22 12A10 10 0 0 0 12 2v10z" />
              </svg>
            </div>
            <CardTitle className="text-2xl text-center">{tierDetails[subscriptionTiers.ENTERPRISE].name}</CardTitle>
            <CardDescription className="text-center">For VC firms and institutions</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <div className="text-center mb-6">
              <span className="text-4xl font-bold">{formatPrice(tierDetails[subscriptionTiers.ENTERPRISE].price)}</span>
              <span className="text-muted-foreground">/month</span>
            </div>
            <ul className="space-y-2">
              {tierDetails[subscriptionTiers.ENTERPRISE].features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => handleSubscribe(subscriptionTiers.ENTERPRISE)}
              isLoading={isLoading[subscriptionTiers.ENTERPRISE]}
              className="w-full"
            >
              Subscribe
            </Button>
          </CardFooter>
        </Card>
      </div>

      <div className="text-center mt-12 max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Frequently Asked Questions</h2>
        <div className="space-y-6 text-left">
          <div>
            <h3 className="text-lg font-medium mb-2">Can I switch plans later?</h3>
            <p className="text-muted-foreground">
              Yes, you can upgrade or downgrade your plan at any time. Changes will be applied to your next billing cycle.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-medium mb-2">Is there a free trial?</h3>
            <p className="text-muted-foreground">
              We offer a 14-day free trial for all new accounts. No credit card required to try the platform.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-medium mb-2">How do I cancel my subscription?</h3>
            <p className="text-muted-foreground">
              You can cancel your subscription from your account settings at any time. You'll continue to have access until the end of your billing period.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}