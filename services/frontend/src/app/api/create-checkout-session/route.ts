import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { subscriptionTiers, tierDetails } from '@/lib/stripe/stripe-client';

// Initialize Stripe
if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('Missing STRIPE_SECRET_KEY environment variable');
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16' as any, // Note: Stripe types may not be up to date
});

export async function POST(request: NextRequest) {
  try {
    // Get the plan ID from the request body
    const { planId } = await request.json();

    // Validate plan ID
    if (!planId || !Object.values(subscriptionTiers).includes(planId)) {
      return NextResponse.json(
        { error: 'Invalid plan ID' },
        { status: 400 }
      );
    }

    // Get the details for the selected plan
    const plan = tierDetails[planId];
    if (!plan) {
      return NextResponse.json(
        { error: 'Plan not found' },
        { status: 400 }
      );
    }

    // In a real app, you'd fetch the current user from the session
    // For this example, we'll use a dummy user ID
    const userId = 'user_123'; // Replace with real user ID from session
    
    // Create a checkout session
    // Note: We're using the pricing page format
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      billing_address_collection: 'auto',
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `AI.VC ${plan.name} Plan`,
              description: 'Monthly subscription',
            },
            unit_amount: plan.price * 100, // Convert dollars to cents
            recurring: {
              interval: 'month',
            },
          },
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: `${request.headers.get('origin') || 'http://localhost:5000'}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${request.headers.get('origin') || 'http://localhost:5000'}/pricing`,
      client_reference_id: userId,
      metadata: {
        plan: planId,
      },
    });

    // Return the session URL to redirect to Stripe checkout
    return NextResponse.json({ url: session.url });
  } catch (error: any) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}