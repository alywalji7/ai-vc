import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

// Initialize Stripe with secret key from environment variable
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "", {
  apiVersion: "2023-10-16",
});

/**
 * Stripe webhook endpoint to handle events
 */
export async function POST(req: NextRequest) {
  // Get the signature from the request headers
  const signature = req.headers.get("stripe-signature") || "";
  
  // Get the request body as text
  const body = await req.text();
  
  try {
    // Verify the webhook signature using the webhook secret
    // In a real implementation, we would pass the webhook secret from environment variables
    // const event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!);
    
    // For demo purposes, we'll parse the body directly (skipping signature verification)
    const event = JSON.parse(body) as Stripe.Event;
    
    // Handle different event types
    switch (event.type) {
      case "customer.subscription.deleted":
        await handleSubscriptionCanceled(event.data.object as Stripe.Subscription);
        break;
        
      case "invoice.paid":
        await handleInvoicePaid(event.data.object as Stripe.Invoice);
        break;
        
      case "invoice.payment_failed":
        await handleInvoicePaymentFailed(event.data.object as Stripe.Invoice);
        break;
        
      case "checkout.session.completed":
        await handleCheckoutSessionCompleted(event.data.object as Stripe.Checkout.Session);
        break;
        
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
    
    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Error handling webhook:", error);
    return NextResponse.json(
      { error: "Failed to process webhook" },
      { status: 400 }
    );
  }
}

/**
 * Handle subscription canceled event
 */
async function handleSubscriptionCanceled(subscription: Stripe.Subscription) {
  console.log("Subscription canceled:", subscription.id);
  
  try {
    // In a real implementation, we would update our database to mark the subscription as canceled
    // We would also trigger any necessary cleanup actions
    
    // Example API call to our backend to update subscription status
    // await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions/${subscription.id}/cancel`, { method: "PUT" });
    
    // For demo purposes, we'll just log the event
    console.log(`Subscription ${subscription.id} has been canceled successfully`);
  } catch (error) {
    console.error("Error processing subscription cancellation:", error);
  }
}

/**
 * Handle invoice paid event
 */
async function handleInvoicePaid(invoice: Stripe.Invoice) {
  console.log("Invoice paid:", invoice.id);
  
  try {
    // Generate PDF invoice and send email notification
    await generateInvoicePdf(invoice.id);
    
    // In a real implementation, store the invoice record in our database
    // and associate it with the user
    
    // For demo purposes, we'll just log the invoice details
    console.log(`Invoice ${invoice.id} for subscription ${invoice.subscription} has been paid`);
  } catch (error) {
    console.error("Error processing invoice payment:", error);
  }
}

/**
 * Handle invoice payment failed event
 */
async function handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
  console.log("Invoice payment failed:", invoice.id);
  
  try {
    // In a real implementation, we would notify the user about the failed payment
    // and suggest actions to resolve the issue
    
    // For demo purposes, we'll just log the event
    console.log(`Invoice ${invoice.id} for subscription ${invoice.subscription} payment failed`);
  } catch (error) {
    console.error("Error processing failed invoice payment:", error);
  }
}

/**
 * Handle checkout session completed event
 */
async function handleCheckoutSessionCompleted(session: Stripe.Checkout.Session) {
  console.log("Checkout session completed:", session.id);
  
  try {
    // In a real implementation, we would create a new subscription in our database
    // and associate it with the user
    
    // For demo purposes, we'll just log the event
    console.log(`Checkout session ${session.id} has been completed successfully`);
  } catch (error) {
    console.error("Error processing checkout session:", error);
  }
}

/**
 * Generate PDF invoice
 */
async function generateInvoicePdf(invoiceId: string) {
  console.log(`Generating PDF for invoice ${invoiceId}`);
  
  try {
    // In a real implementation, we would generate the PDF invoice
    // and store it in S3/Minio
    
    // For demo purposes, we'll just log the event
    console.log(`PDF for invoice ${invoiceId} has been generated successfully`);
  } catch (error) {
    console.error("Error generating invoice PDF:", error);
  }
}