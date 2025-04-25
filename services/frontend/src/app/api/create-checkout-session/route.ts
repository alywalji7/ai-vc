import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

// Initialize Stripe with secret key from environment variable
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "", {
  apiVersion: "2023-10-16",
});

// Define subscription tiers with features
const SUBSCRIPTION_TIERS = {
  starter: {
    name: "Starter",
    price: 500,
    features: ["1 Seat", "$500 Transaction Limit", "50 API Calls/Day"]
  },
  pro: {
    name: "Pro",
    price: 1000,
    features: ["3 Seats", "$1,000 Transaction Limit", "500 API Calls/Day"]
  },
  enterprise: {
    name: "Enterprise",
    price: 2000,
    features: ["Unlimited Seats", "$2,000 Transaction Limit", "10,000 API Calls/Day"]
  }
};

export async function POST(req: NextRequest) {
  try {
    const { tier } = await req.json();
    
    // Get the selected tier details
    const tierDetails = SUBSCRIPTION_TIERS[tier];
    
    if (!tierDetails) {
      return NextResponse.json(
        { error: "Invalid subscription tier" },
        { status: 400 }
      );
    }
    
    // Create a Stripe checkout session (simplified for demo)
    // In a real implementation, this would create a real checkout session using the Stripe API
    
    // Example success and cancel URLs
    const baseUrl = req.headers.get("origin") || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:5000";
    const successUrl = `${baseUrl}/settings/billing?success=true`;
    const cancelUrl = `${baseUrl}/pricing?canceled=true`;
    
    // Mock checkout session URL (in production, this would be a real Stripe checkout URL)
    const mockCheckoutSessionUrl = `https://checkout.stripe.com/c/pay/mock_session_${Date.now()}`;
    
    return NextResponse.json({ url: mockCheckoutSessionUrl });
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 }
    );
  }
}