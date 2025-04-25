import { NextRequest, NextResponse } from 'next/server';

// Environment variables
const UPLOAD_SERVICE_URL = process.env.UPLOAD_SERVICE_URL || 'http://localhost:8400';

/**
 * GET handler for retrieving fund positions for an LP
 * Proxies the request to the upload service
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { lpId: string } }
) {
  try {
    const { lpId } = params;
    
    // Forward the request to the upload service
    const response = await fetch(`${UPLOAD_SERVICE_URL}/api/v1/funds/${lpId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch fund positions' },
        { status: response.status }
      );
    }
    
    const responseData = await response.json();
    return NextResponse.json(responseData);
    
  } catch (error: any) {
    console.error('Error fetching fund positions:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}