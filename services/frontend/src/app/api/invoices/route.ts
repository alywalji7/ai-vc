import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";

/**
 * API endpoint to get invoice history for a user
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
    // For this demo, we'll return mock invoice data
    const mockInvoices = [
      {
        id: "inv_123456",
        amount: 1000.00,
        currency: "usd",
        status: "paid",
        created: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        pdf: "https://example.com/invoice_123456.pdf",
      },
      {
        id: "inv_123455",
        amount: 1000.00,
        currency: "usd",
        status: "paid",
        created: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
        pdf: "https://example.com/invoice_123455.pdf",
      },
      {
        id: "inv_123454",
        amount: 1000.00,
        currency: "usd",
        status: "paid",
        created: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
        pdf: "https://example.com/invoice_123454.pdf",
      }
    ];
    
    return NextResponse.json(mockInvoices);
  } catch (error) {
    console.error("Error fetching invoices:", error);
    return NextResponse.json(
      { error: "Failed to fetch invoice history" },
      { status: 500 }
    );
  }
}