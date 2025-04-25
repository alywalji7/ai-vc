import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";

/**
 * API endpoint to get subscription details for a user
 */
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  
  if (!session?.user?.id) {
    return NextResponse.json(
      { error: "Authentication required" },
      { status: 401 }
    );
  }

  try {
    // In a real implementation, this would fetch from the billing service
    // For now, we'll return a mock subscription
    const mockSubscription = {
      id: "sub_123456",
      tier: "pro",
      status: "active",
      currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      seats: {
        limit: 3,
        used: 2,
      },
      apiUsage: {
        daily: {
          limit: 500,
          used: 123,
        }
      }
    };
    
    return NextResponse.json(mockSubscription);
  } catch (error) {
    console.error("Error fetching subscription:", error);
    return NextResponse.json(
      { error: "Failed to fetch subscription details" },
      { status: 500 }
    );
  }
}