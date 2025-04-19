import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * GET handler for retrieving details of a specific data room
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { companyId: string } }
) {
  try {
    const companyId = params.companyId;
    
    // Build the API URL
    const apiUrl = `${BACKEND_URL}/api/dataroom/${companyId}`;
    
    // Fetch data from the backend
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching dataroom: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    // Return the data
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in dataroom details API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}