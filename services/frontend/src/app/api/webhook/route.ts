import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

// Initialize Stripe
if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('Missing STRIPE_SECRET_KEY environment variable');
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16' as any, // Note: Stripe types may not be up to date
});

// This is your Stripe webhook secret for testing your endpoint locally.
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

export async function POST(request: NextRequest) {
  const payload = await request.text();
  const signature = request.headers.get('stripe-signature') as string;

  let event: Stripe.Event;

  try {
    if (!endpointSecret) {
      throw new Error('STRIPE_WEBHOOK_SECRET is not set');
    }

    event = stripe.webhooks.constructEvent(payload, signature, endpointSecret);
  } catch (err: any) {
    console.error(`⚠️ Webhook signature verification failed: ${err.message}`);
    return NextResponse.json({ error: err.message }, { status: 400 });
  }

  // Handle the event
  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        
        if (session.mode === 'subscription') {
          // If subscription, update user subscription status in database
          await handleCompletedCheckoutSession(session);
        }
        break;
      }
      
      case 'customer.subscription.created': {
        const subscription = event.data.object as Stripe.Subscription;
        
        // Update user subscription in database
        await handleSubscriptionCreated(subscription);
        break;
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        
        // Update user subscription in database
        await handleSubscriptionUpdated(subscription);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        
        // Mark user subscription as cancelled in database
        await handleSubscriptionDeleted(subscription);
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice;
        
        // Handle successful payment
        if (invoice.subscription) {
          await handleInvoicePaymentSucceeded(invoice);
        }
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;
        
        // Handle failed payment
        if (invoice.subscription) {
          await handleInvoicePaymentFailed(invoice);
        }
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error(`Error handling webhook event: ${error}`);
    return NextResponse.json(
      { error: 'Error handling webhook event' },
      { status: 500 }
    );
  }
}

// Helper functions to handle Stripe events
// In a real application, these would update your database

async function handleCompletedCheckoutSession(session: Stripe.Checkout.Session) {
  // Implementation would:
  // 1. Get user from client_reference_id
  // 2. Store subscription details in your database
  console.log(`Processing completed checkout session: ${session.id}`);
  
  // This is where you would call an API endpoint to update the user's subscription
  // const userId = session.client_reference_id;
  // const subscriptionId = session.subscription;
  // await updateUserSubscription(userId, subscriptionId);
}

async function handleSubscriptionCreated(subscription: Stripe.Subscription) {
  console.log(`Subscription created: ${subscription.id}`);
  // Update user's subscription status to active
  // const customerId = subscription.customer;
  // await updateCustomerSubscriptionStatus(customerId, subscription.id, 'active');
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  console.log(`Subscription updated: ${subscription.id}`);
  
  // Update subscription status based on the new status
  const status = subscription.status;
  // const customerId = subscription.customer;
  // await updateCustomerSubscriptionStatus(customerId, subscription.id, status);
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  console.log(`Subscription deleted: ${subscription.id}`);
  
  // Mark subscription as cancelled in your database
  // const customerId = subscription.customer;
  // await updateCustomerSubscriptionStatus(customerId, subscription.id, 'cancelled');
}

async function handleInvoicePaymentSucceeded(invoice: Stripe.Invoice) {
  console.log(`Invoice payment succeeded: ${invoice.id}`);
  
  // Update subscription payment history
  // const customerId = invoice.customer;
  // const subscriptionId = invoice.subscription;
  // await recordSuccessfulPayment(customerId, subscriptionId, invoice.id, invoice.amount_paid);
}

async function handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
  console.log(`Invoice payment failed: ${invoice.id}`);
  
  // Record failed payment and potentially notify the user
  // const customerId = invoice.customer;
  // const subscriptionId = invoice.subscription;
  // await recordFailedPayment(customerId, subscriptionId, invoice.id);
  // await sendPaymentFailureNotification(customerId);
}